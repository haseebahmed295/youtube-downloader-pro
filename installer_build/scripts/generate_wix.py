# coding: utf-8
"""
Generate WiX installer.wxs file with all files from PyInstaller dist folder
Organized build structure
"""
import os
import uuid
from pathlib import Path

# Get absolute paths
SCRIPT_DIR = Path(__file__).parent.absolute()
PROJECT_ROOT = SCRIPT_DIR.parent.parent
DIST_DIR = PROJECT_ROOT / "dist" / "YouTube Downloader Pro"
OUTPUT_FILE = SCRIPT_DIR.parent / "temp" / "installer_generated.wxs"
ASSETS_DIR = SCRIPT_DIR.parent / "assets"

def generate_component_id(file_path):
    """Generate a unique component ID from file path"""
    path_str = str(file_path).replace("\\", "_").replace("/", "_").replace(".", "_").replace(" ", "_").replace("-", "_")
    return f"Comp_{path_str}"[:72]

def generate_file_id(file_path):
    """Generate a unique file ID"""
    path_str = str(file_path).replace("\\", "_").replace("/", "_").replace(".", "_").replace(" ", "_").replace("-", "_")
    return f"File_{path_str}"[:72]

def scan_directory(base_path, current_path=""):
    """Recursively scan directory and return file list"""
    files = []
    full_path = base_path / current_path if current_path else base_path
    
    if not full_path.exists():
        return files
    
    for item in full_path.iterdir():
        rel_path = Path(current_path) / item.name if current_path else Path(item.name)
        
        if item.is_file():
            files.append(rel_path)
        elif item.is_dir():
            files.extend(scan_directory(base_path, rel_path))
    
    return files

def get_directory_structure(files):
    """Build directory structure from file list"""
    dirs = set()
    for f in files:
        parts = Path(f).parts
        for i in range(len(parts)):
            dir_path = Path(*parts[:i+1])
            if dir_path != Path(f):
                dirs.add(str(dir_path))
    return sorted(dirs)

def generate_wix_xml():
    """Generate complete WiX XML"""
    
    if not DIST_DIR.exists():
        print(f"ERROR: {DIST_DIR} not found!")
        print("Run PyInstaller first: pyinstaller youtube_downloader.spec")
        return False
    
    print("Scanning files...")
    all_files = scan_directory(DIST_DIR)
    print(f"Found {len(all_files)} files")
    
    # Separate main exe from other files
    main_exe = None
    other_files = []
    
    for f in all_files:
        if f.name == "YouTube Downloader Pro.exe":
            main_exe = f
        else:
            other_files.append(f)
    
    if not main_exe:
        print("ERROR: Main executable not found!")
        return False
    
    directories = get_directory_structure(other_files)
    print(f"Found {len(directories)} directories")
    
    # Build directory IDs
    dir_ids = {'': 'INSTALLFOLDER'}
    for dir_path in directories:
        clean_path = dir_path.replace('/', '_').replace('\\', '_').replace(' ', '_').replace('-', '_').replace('.', '_')
        dir_id = f"Dir_{clean_path}"
        dir_ids[dir_path] = dir_id
    
    # Start building XML
    xml_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<Wix xmlns="http://wixtoolset.org/schemas/v4/wxs"',
        '     xmlns:ui="http://wixtoolset.org/schemas/v4/wxs/ui">',
        '',
        '  <Package Name="YouTube Downloader Pro"',
        '           Language="1033"',
        '           Version="1.0.0.0"',
        '           Manufacturer="Haseeb Ahmed"',
        '           UpgradeCode="A7B8C9D0-E1F2-4A5B-8C9D-0E1F2A3B4C5D"',
        '           InstallerVersion="500"',
        '           Compressed="yes"',
        '           Scope="perMachine">',
        '',
        '    <MajorUpgrade DowngradeErrorMessage="A newer version of [ProductName] is already installed." />',
        '    <MediaTemplate EmbedCab="yes" />',
        '',
        '    <Feature Id="ProductFeature" Title="YouTube Downloader Pro" Level="1">',
        '      <ComponentGroupRef Id="ProductComponents" />',
    ]
    
    # Group files by directory
    files_by_dir = {}
    for f in other_files:
        dir_path = str(f.parent) if f.parent != Path('.') else ""
        if dir_path not in files_by_dir:
            files_by_dir[dir_path] = []
        files_by_dir[dir_path].append(f)
    
    dirs_with_files = sorted(files_by_dir.keys())
    for dir_path in dirs_with_files:
        dir_id = dir_ids.get(dir_path, 'INSTALLFOLDER')
        xml_lines.append(f'      <ComponentGroupRef Id="CG_{dir_id}" />')
    
    # Convert paths to strings with proper separators
    license_path = str(ASSETS_DIR / "license.rtf").replace("/", "\\")
    banner_path = str(ASSETS_DIR / "installer_banner.bmp").replace("/", "\\")
    dialog_path = str(ASSETS_DIR / "installer_dialog.bmp").replace("/", "\\")
    icon_path = str(ASSETS_DIR / "app_icon.ico").replace("/", "\\")
    
    xml_lines.extend([
        '      <ComponentGroupRef Id="ApplicationShortcuts" />',
        '    </Feature>',
        '',
        '    <ui:WixUI Id="WixUI_InstallDir" />',
        '    <Property Id="WIXUI_INSTALLDIR" Value="INSTALLFOLDER" />',
        f'    <WixVariable Id="WixUILicenseRtf" Value="{license_path}" />',
        f'    <WixVariable Id="WixUIBannerBmp" Value="{banner_path}" />',
        f'    <WixVariable Id="WixUIDialogBmp" Value="{dialog_path}" />',
        '',
        f'    <Icon Id="AppIcon" SourceFile="{icon_path}" />',
        '    <Property Id="ARPPRODUCTICON" Value="AppIcon" />',
        '    <Property Id="ARPHELPLINK" Value="https://github.com/haseebahmed295/youtube-downloader-pro" />',
        '    <Property Id="ARPURLINFOABOUT" Value="https://github.com/haseebahmed295/youtube-downloader-pro" />',
        '',
    ])
    
    # Build nested directory structure
    xml_lines.append('    <StandardDirectory Id="ProgramFiles6432Folder">')
    xml_lines.append('      <Directory Id="INSTALLFOLDER" Name="YouTube Downloader Pro">')
    
    def add_directories(parent_path, indent_level):
        indent = '        ' + ('  ' * indent_level)
        children = [d for d in directories if Path(d).parent == Path(parent_path) or (parent_path == '' and len(Path(d).parts) == 1)]
        for child_dir in sorted(set(children)):
            dir_id = dir_ids[child_dir]
            dir_name = Path(child_dir).name
            xml_lines.append(f'{indent}<Directory Id="{dir_id}" Name="{dir_name}">')
            sub_children = [d for d in directories if str(Path(d).parent) == child_dir]
            if sub_children:
                add_directories(child_dir, indent_level + 1)
            xml_lines.append(f'{indent}</Directory>')
    
    add_directories('', 0)
    
    xml_lines.extend([
        '      </Directory>',
        '    </StandardDirectory>',
        '    <StandardDirectory Id="ProgramMenuFolder">',
        '      <Directory Id="ApplicationProgramsFolder" Name="YouTube Downloader Pro"/>',
        '    </StandardDirectory>',
        '    <StandardDirectory Id="DesktopFolder" />',
        '',
        '  </Package>',
        '',
    ])
    
    # Main executable fragment
    main_exe_path = str(DIST_DIR / main_exe).replace("/", "\\")
    
    xml_lines.extend([
        '  <!-- Main Executable -->',
        '  <Fragment>',
        '    <ComponentGroup Id="ProductComponents" Directory="INSTALLFOLDER">',
        f'      <Component Id="MainExecutable">',
        f'        <File Id="MainExeFile" Source="{main_exe_path}" KeyPath="yes">',
        '          <Shortcut Id="StartMenuShortcut"',
        '                    Directory="ApplicationProgramsFolder"',
        '                    Name="YouTube Downloader Pro"',
        '                    Description="Download YouTube videos and audio"',
        '                    WorkingDirectory="INSTALLFOLDER"',
        '                    Icon="AppIcon" />',
        '          <Shortcut Id="DesktopShortcut"',
        '                    Directory="DesktopFolder"',
        '                    Name="YouTube Downloader Pro"',
        '                    Description="Download YouTube videos and audio"',
        '                    WorkingDirectory="INSTALLFOLDER"',
        '                    Icon="AppIcon" />',
        '        </File>',
        '      </Component>',
        '    </ComponentGroup>',
        '  </Fragment>',
        '',
    ])
    
    # Add component groups for each directory
    print("Generating components...")
    for dir_path in dirs_with_files:
        files = files_by_dir[dir_path]
        dir_id = dir_ids.get(dir_path, 'INSTALLFOLDER')
        
        xml_lines.append('  <Fragment>')
        xml_lines.append(f'    <ComponentGroup Id="CG_{dir_id}" Directory="{dir_id}">')
        
        for file_path in files:
            comp_id = generate_component_id(file_path)
            file_id = generate_file_id(file_path)
            source_path = str(DIST_DIR / file_path).replace("/", "\\")
            file_name = Path(file_path).name
            unique_guid = str(uuid.uuid5(uuid.NAMESPACE_DNS, str(file_path)))
            
            xml_lines.append(f'      <Component Id="{comp_id}" Guid="{unique_guid}">')
            xml_lines.append(f'        <File Id="{file_id}" Source="{source_path}" Name="{file_name}" />')
            xml_lines.append('      </Component>')
        
        xml_lines.append('    </ComponentGroup>')
        xml_lines.append('  </Fragment>')
        xml_lines.append('')
    
    xml_lines.extend([
        '  <Fragment>',
        '    <ComponentGroup Id="ApplicationShortcuts" Directory="ApplicationProgramsFolder">',
        '      <Component Id="ApplicationShortcutsComponent">',
        '        <RemoveFolder Id="CleanUpShortCut" Directory="ApplicationProgramsFolder" On="uninstall"/>',
        '        <RegistryValue Root="HKCU"',
        '                       Key="Software\\YouTube Downloader Pro"',
        '                       Name="installed"',
        '                       Type="integer"',
        '                       Value="1"',
        '                       KeyPath="yes"/>',
        '      </Component>',
        '    </ComponentGroup>',
        '  </Fragment>',
        '',
        '</Wix>',
    ])
    
    # Write to file
    print(f"Writing {OUTPUT_FILE}...")
    output_path = Path(__file__).parent / OUTPUT_FILE
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(xml_lines))
    
    print(f"SUCCESS! Generated {output_path}")
    print(f"Total components: {len(other_files) + 1}")
    return True

if __name__ == "__main__":
    print("=" * 50)
    print("WiX Installer Generator")
    print("=" * 50)
    print()
    
    if generate_wix_xml():
        print()
        print("Next step: Run build.bat")
    else:
        print()
        print("Generation failed!")
