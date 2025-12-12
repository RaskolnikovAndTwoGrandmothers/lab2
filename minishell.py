import os
import sys
import shutil
import logging
from datetime import datetime

class MiniShell:
    def __init__(self):
        self.current_dir = os.getcwd()
        self.setup_logging()
    
    def setup_logging(self):
        logging.basicConfig(
            filename='shell.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
    
    def log_command(self, command, success=True, error=""):
        status = "SUCCESS" if success else "FAILED"
        log_msg = f"{status}: {command}"
        if error:
            log_msg += f" | Error: {error}"
        logging.info(log_msg)
    
    def ls(self, path=None, detailed=False):
        try:
            target_path = path if path else self.current_dir
            if not os.path.exists(target_path):
                raise FileNotFoundError(f"Path not found: {target_path}")
            
            items = os.listdir(target_path)
            if detailed:
                for item in items:
                    full_path = os.path.join(target_path, item)
                    if os.path.exists(full_path):
                        stat = os.stat(full_path)
                        size = stat.st_size
                        mtime = datetime.fromtimestamp(stat.st_mtime)
                        perms = oct(stat.st_mode)[-3:]
                        print(f"{item:20} {size:10} {mtime:%Y-%m-%d %H:%M:%S} {perms}")
            else:
                print('\n'.join(items))
            
            self.log_command(f"ls {'-l ' if detailed else ''}{path if path else ''}", success=True)
        except Exception as e:
            print(f"Error: {e}")
            self.log_command(f"ls {path if path else ''}", success=False, error=str(e))
    
    def cd(self, path):
        try:
            if path == "..":
                new_dir = os.path.dirname(self.current_dir)
            elif path == "~":
                new_dir = os.path.expanduser("~")
            else:
                new_dir = os.path.join(self.current_dir, path)
            
            new_dir = os.path.abspath(new_dir)
            
            if not os.path.exists(new_dir):
                raise FileNotFoundError(f"Directory not found: {new_dir}")
            if not os.path.isdir(new_dir):
                raise NotADirectoryError(f"Not a directory: {new_dir}")
            
            self.current_dir = new_dir
            print(f"Current directory: {self.current_dir}")
            self.log_command(f"cd {path}", success=True)
        except Exception as e:
            print(f"Error: {e}")
            self.log_command(f"cd {path}", success=False, error=str(e))
    
    def cat(self, file_path):
        try:
            full_path = os.path.join(self.current_dir, file_path)
            if not os.path.exists(full_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            if os.path.isdir(full_path):
                raise IsADirectoryError(f"{file_path} is a directory")
            
            with open(full_path, 'r', encoding='utf-8') as f:
                print(f.read())
            
            self.log_command(f"cat {file_path}", success=True)
        except Exception as e:
            print(f"Error: {e}")
            self.log_command(f"cat {file_path}", success=False, error=str(e))
    
    def cp(self, source, dest, recursive=False):
        try:
            src_path = os.path.join(self.current_dir, source)
            dst_path = os.path.join(self.current_dir, dest)
            
            if not os.path.exists(src_path):
                raise FileNotFoundError(f"Source not found: {source}")
            
            if recursive and os.path.isdir(src_path):
                if os.path.exists(dst_path):
                    dest_dir = dst_path if os.path.isdir(dst_path) else os.path.dirname(dst_path)
                    dest_name = os.path.basename(src_path)
                    dst_path = os.path.join(dest_dir, dest_name)
                shutil.copytree(src_path, dst_path)
            else:
                shutil.copy2(src_path, dst_path)
            
            print(f"Copied {source} to {dest}")
            self.log_command(f"cp {'-r ' if recursive else ''}{source} {dest}", success=True)
        except Exception as e:
            print(f"Error: {e}")
            self.log_command(f"cp {source} {dest}", success=False, error=str(e))
    
    def mv(self, source, dest):
        try:
            src_path = os.path.join(self.current_dir, source)
            dst_path = os.path.join(self.current_dir, dest)
            
            if not os.path.exists(src_path):
                raise FileNotFoundError(f"Source not found: {source}")
            
            shutil.move(src_path, dst_path)
            print(f"Moved {source} to {dest}")
            self.log_command(f"mv {source} {dest}", success=True)
        except Exception as e:
            print(f"Error: {e}")
            self.log_command(f"mv {source} {dest}", success=False, error=str(e))
    
    def rm(self, target, recursive=False):
        try:
            target_path = os.path.join(self.current_dir, target)
            
            if not os.path.exists(target_path):
                raise FileNotFoundError(f"Target not found: {target}")
            
            root_dir = os.path.abspath('/')
            if os.path.abspath(target_path) == root_dir:
                raise PermissionError("Cannot delete root directory")
            
            parent_dir = os.path.dirname(self.current_dir)
            if os.path.abspath(target_path) == parent_dir:
                raise PermissionError("Cannot delete parent directory")
            
            if os.path.isdir(target_path) and recursive:
                confirm = input(f"Delete directory '{target}' recursively? (y/n): ")
                if confirm.lower() == 'y':
                    shutil.rmtree(target_path)
                    print(f"Removed directory: {target}")
                else:
                    print("Cancelled")
            elif os.path.isdir(target_path):
                raise IsADirectoryError(f"Use -r option to delete directory: {target}")
            else:
                os.remove(target_path)
                print(f"Removed file: {target}")
            
            self.log_command(f"rm {'-r ' if recursive else ''}{target}", success=True)
        except Exception as e:
            print(f"Error: {e}")
            self.log_command(f"rm {target}", success=False, error=str(e))
    
    def run(self):
        print("MiniShell started. Type 'exit' to quit.")
        print(f"Current directory: {self.current_dir}")
        
        while True:
            try:
                user_input = input(f"\n{os.path.basename(self.current_dir)}> ").strip()
                if not user_input:
                    continue
                
                if user_input.lower() == 'exit':
                    print("Goodbye!")
                    break
                
                parts = user_input.split()
                command = parts[0].lower()
                args = parts[1:]
                
                if command == 'ls':
                    detailed = '-l' in args
                    path_args = [arg for arg in args if arg != '-l']
                    path = path_args[0] if path_args else None
                    self.ls(path, detailed)
                elif command == 'cd' and args:
                    self.cd(args[0])
                elif command == 'cat' and args:
                    self.cat(args[0])
                elif command == 'cp' and len(args) >= 2:
                    recursive = '-r' in args
                    file_args = [arg for arg in args if arg != '-r']
                    if len(file_args) < 2:
                        print("Usage: cp [-r] source dest")
                        continue
                    source = file_args[0]
                    dest = file_args[1]
                    self.cp(source, dest, recursive)
                elif command == 'mv' and len(args) == 2:
                    self.mv(args[0], args[1])
                elif command == 'rm' and args:
                    recursive = '-r' in args
                    target_args = [arg for arg in args if arg != '-r']
                    if not target_args:
                        print("Usage: rm [-r] target")
                        continue
                    target = target_args[0]
                    self.rm(target, recursive)
                else:
                    print(f"Unknown command or invalid arguments: {command}")
                    self.log_command(user_input, success=False, error="Unknown command")
            
            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                break
            except Exception as e:
                print(f"Unexpected error: {e}")
                logging.error(f"Unexpected error: {e}")

if __name__ == "__main__":
    shell = MiniShell()
    shell.run()
