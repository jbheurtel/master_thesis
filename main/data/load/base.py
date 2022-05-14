from main.parameters.base import get_params

# loads from prepped data, based on parameters.

def load_data(workspace_root):
    params = get_params(workspace_root)


if __name__ == "__main__":
    workspace_root = r"/Users/jean-baptisteheurtel/Main/university/masters/Thesis/02_workspace/test_ws_2"
    load_data(workspace_root)