import json
import sys
import io
import traceback
import os

def run_notebook():
    notebook_path = "MyTravelHelper_v2_Multilingual.ipynb"
    if not os.path.exists(notebook_path):
        print(f"Error: {notebook_path} does not exist.")
        return
        
    with open(notebook_path, "r", encoding="utf-8") as f:
        nb = json.load(f)

    # Set up global dict to share variables/imports across cells
    # Also load dotenv and adjust sys.path so modules are found
    from dotenv import load_dotenv
    load_dotenv()
    sys.path.append(os.getcwd())
    
    globals_dict = {
        "__builtins__": __builtins__,
        "__file__": "notebook.ipynb"
    }

    print("Executing code cells sequentially in shared context...")
    exec_count = 1
    for idx, cell in enumerate(nb["cells"]):
        if cell["cell_type"] == "code":
            code = "".join(cell["source"])
            print(f"Running cell {idx}...")
            
            stdout_capture = io.StringIO()
            stderr_capture = io.StringIO()
            
            # Backup stdout and stderr
            old_stdout = sys.stdout
            old_stderr = sys.stderr
            
            # Redirect to capture outputs
            sys.stdout = stdout_capture
            sys.stderr = stderr_capture
            
            try:
                # Execute code in global namespace
                exec(code, globals_dict)
            except Exception:
                # Capture exception traceback
                traceback.print_exc(file=stderr_capture)
            finally:
                # Restore stdout and stderr
                sys.stdout = old_stdout
                sys.stderr = old_stderr
                
            outputs = []
            stdout_val = stdout_capture.getvalue()
            stderr_val = stderr_capture.getvalue()
            
            if stdout_val:
                outputs.append({
                    "name": "stdout",
                    "output_type": "stream",
                    "text": [line + "\n" for line in stdout_val.splitlines()]
                })
            if stderr_val:
                # Clean up verbose warnings to keep notebook outputs readable
                clean_stderr = [line for line in stderr_val.splitlines() if "warning" not in line.lower()]
                if clean_stderr:
                    outputs.append({
                        "name": "stderr",
                        "output_type": "stream",
                        "text": [line + "\n" for line in clean_stderr]
                    })
                    
            cell["outputs"] = outputs
            cell["execution_count"] = exec_count
            exec_count += 1

    with open(notebook_path, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=2, ensure_ascii=False)

    print(f"Notebook execution complete. Saved outputs back to {notebook_path}!")

if __name__ == "__main__":
    run_notebook()
