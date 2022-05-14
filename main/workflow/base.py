from main.workflow.workspace import WorkSpace
from main.parameters.base import ParamLoader

if __name__ == '__main__':
    params = ParamLoader("2")
    WorkSpace(params)
