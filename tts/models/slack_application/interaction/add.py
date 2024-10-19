from pydantic import BaseModel


class ElementInput(BaseModel):
    type: str
    value: str


class WorkspaceNameBlock(BaseModel):
    workspace_name: ElementInput


class WorkspaceEmailBlock(BaseModel):
    workspace_email: ElementInput


class ViewState(BaseModel):
    values: dict[str, dict[str, ElementInput]]


class View(BaseModel):
    callback_id: str
    state: ViewState


class User(BaseModel):
    id: str
    username: str
    name: str
    team_id: str


class Team(BaseModel):
    id: str
    domain: str


class SlackInteractionModalResponse(BaseModel):
    type: str
    team: Team
    user: User
    api_app_id: str
    trigger_id: str
    view: View
