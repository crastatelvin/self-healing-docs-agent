from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import threading
import os
from utils.watcher import FileWatcher
from agents.graph import create_graph

app = FastAPI()

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state to keep track of current analysis
analysis_results = []
graph = create_graph()

class PatchApproval(BaseModel):
    file_path: str
    approved: bool

def on_file_change(file_path):
    print(f"Main received change for: {file_path}")
    # Read the file content
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        # In a real scenario, we'd compare with previous version or git diff
        # For this demo, we'll just send the new content
        initial_state = {
            "file_path": file_path,
            "changed_code": content,
            "old_code": "", # Placeholder
            "status": "starting"
        }
        
        # Invoke the LangGraph
        # Note: In production, you'd handle this as an async task
        result = graph.invoke(initial_state)
        analysis_results.append(result)
        print(f"Analysis complete for {file_path}")
        
    except Exception as e:
        print(f"Error processing file change: {e}")

@app.on_event("startup")
async def startup_event():
    # Use absolute path to ensure we are watching the right place
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(backend_dir)
    
    print(f"DEBUG: Backend Dir: {backend_dir}")
    print(f"DEBUG: Project Root (Watching): {project_root}")
    
    watcher = FileWatcher(project_root, on_file_change)
    thread = threading.Thread(target=watcher.start, daemon=True)
    thread.start()
    print("File watcher started on startup.")

@app.get("/results")
async def get_results():
    return analysis_results

@app.post("/approve")
async def approve_patch(approval: PatchApproval):
    # In a real scenario, this would write the patch to the .md file
    if approval.approved:
        # Logic to apply patch would go here
        return {"status": "Patch applied successfully"}
    return {"status": "Patch rejected"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
