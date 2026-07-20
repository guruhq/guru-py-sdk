"""Auto-generated Pydantic v2 models from the Guru public API spec.

DO NOT EDIT BY HAND. Re-generate with:
    python scripts/generate_models.py

Source: swagger/swagger.json
"""

from __future__ import annotations

from enum import Enum
from typing import Annotated, Any
from uuid import UUID

from pydantic import AwareDatetime, Field, RootModel

from guru_sdk.models._base import GuruModel


class Model(RootModel[Any]):
    root: Any


class FieldModel(Enum):
    datecreated = "DATECREATED"
    nextverification = "NEXTVERIFICATION"
    lastverified = "LASTVERIFIED"
    lastmodified = "LASTMODIFIED"
    first_comment_created_event = "FIRST_COMMENT_CREATED_EVENT"
    last_comment_created_event = "LAST_COMMENT_CREATED_EVENT"
    first_card_copied_event = "FIRST_CARD_COPIED_EVENT"
    last_card_copied_event = "LAST_CARD_COPIED_EVENT"
    last_card_viewed_event = "LAST_CARD_VIEWED_EVENT"
    first_card_viewed_event = "FIRST_CARD_VIEWED_EVENT"


class Op(Enum):
    gt = "GT"
    gte = "GTE"
    lt = "LT"
    lte = "LTE"


class AgentRequest(GuruModel):
    prompt: str | None = None


class Type(Enum):
    search = "SEARCH"
    question = "QUESTION"
    task = "TASK"


class AgentResponse(GuruModel):
    type: Type


class AgentSearchResponse(AgentResponse):
    pass


class AgentTaskResponse(AgentResponse):
    pass


class AiEvaluation(GuruModel):
    id: UUID | None = None
    name: str | None = None
    description: str | None = None
    question: str | None = None
    expected_answer: Annotated[str | None, Field(alias="expectedAnswer")] = None
    created_date: Annotated[AwareDatetime | None, Field(alias="createdDate")] = None
    last_passed_date: Annotated[AwareDatetime | None, Field(alias="lastPassedDate")] = None


class AiEvaluationCreateRequest(GuruModel):
    answer_id: Annotated[UUID | None, Field(alias="answerId")] = None
    name: str | None = None
    description: str | None = None


class UserType(Enum):
    user = "USER"
    knowledge_agent = "KNOWLEDGE_AGENT"


class Status(Enum):
    active = "ACTIVE"
    pending = "PENDING"


class LatestFeedback(Enum):
    thumbs_up = "THUMBS_UP"
    thumbs_down = "THUMBS_DOWN"
    thumbs_up_unselected = "THUMBS_UP_UNSELECTED"
    thumbs_down_unselected = "THUMBS_DOWN_UNSELECTED"


class Status1(Enum):
    answered = "ANSWERED"
    not_answered = "NOT_ANSWERED"
    assigned = "ASSIGNED"
    flagged = "FLAGGED"
    helpful = "HELPFUL"
    all = "ALL"
    my_assigned = "MY_ASSIGNED"
    archived = "ARCHIVED"


class Restriction(Enum):
    mcp_tools_used = "MCP_TOOLS_USED"


class ThreadType(Enum):
    chat = "CHAT"
    slack = "SLACK"
    answer = "ANSWER"


class Feedback(Enum):
    thumbs_up = "THUMBS_UP"
    thumbs_down = "THUMBS_DOWN"
    thumbs_up_unselected = "THUMBS_UP_UNSELECTED"
    thumbs_down_unselected = "THUMBS_DOWN_UNSELECTED"


class AuthorsFacet(GuruModel):
    id: str | None = None
    name: str | None = None
    count: int | None = None


class Op1(Enum):
    wasautoarchived = "WASAUTOARCHIVED"
    wasnotautoarchived = "WASNOTAUTOARCHIVED"
    ispendingautoarchive = "ISPENDINGAUTOARCHIVE"
    isnotpendingautoarchive = "ISNOTPENDINGAUTOARCHIVE"


class Status2(Enum):
    active = "ACTIVE"
    archived = "ARCHIVED"


class Permission(Enum):
    agent_delete = "AGENT_DELETE"
    agent_manage_permissions = "AGENT_MANAGE_PERMISSIONS"
    agent_manage_questions = "AGENT_MANAGE_QUESTIONS"
    agent_manage_settings = "AGENT_MANAGE_SETTINGS"
    agent_view = "AGENT_VIEW"
    agent_view_analytics = "AGENT_VIEW_ANALYTICS"
    agent_verify_sources = "AGENT_VERIFY_SOURCES"
    collection_view = "COLLECTION_VIEW"
    collection_card_verify = "COLLECTION_CARD_VERIFY"
    collection_create_drafts = "COLLECTION_CREATE_DRAFTS"
    collection_publish = "COLLECTION_PUBLISH"
    collection_card_comment = "COLLECTION_CARD_COMMENT"
    collection_card_unverify = "COLLECTION_CARD_UNVERIFY"
    collection_manage_card_settings = "COLLECTION_MANAGE_CARD_SETTINGS"
    collection_manage_card_permissions = "COLLECTION_MANAGE_CARD_PERMISSIONS"
    collection_announcement = "COLLECTION_ANNOUNCEMENT"
    collection_card_archive = "COLLECTION_CARD_ARCHIVE"
    collection_card_delete = "COLLECTION_CARD_DELETE"
    collection_create_draft_existing = "COLLECTION_CREATE_DRAFT_EXISTING"
    collection_create_folders = "COLLECTION_CREATE_FOLDERS"
    collection_manage_folders = "COLLECTION_MANAGE_FOLDERS"
    collection_manage_folder_permissions = "COLLECTION_MANAGE_FOLDER_PERMISSIONS"
    collection_folder_delete = "COLLECTION_FOLDER_DELETE"
    collection_delete = "COLLECTION_DELETE"
    collection_manage_cards = "COLLECTION_MANAGE_CARDS"
    collection_manage_settings = "COLLECTION_MANAGE_SETTINGS"
    collection_manage_permissions = "COLLECTION_MANAGE_PERMISSIONS"
    collection_view_user_analytics = "COLLECTION_VIEW_USER_ANALYTICS"
    collection_view_card_analytics = "COLLECTION_VIEW_CARD_ANALYTICS"
    collection_view_author_analytics = "COLLECTION_VIEW_AUTHOR_ANALYTICS"
    collection_manage_tags = "COLLECTION_MANAGE_TAGS"
    collection_manage_templates = "COLLECTION_MANAGE_TEMPLATES"
    group_delete = "GROUP_DELETE"
    group_manage = "GROUP_MANAGE"
    kt_delete = "KT_DELETE"
    kt_edit = "KT_EDIT"
    kt_manage_permissions = "KT_MANAGE_PERMISSIONS"
    kt_view = "KT_VIEW"
    page_delete = "PAGE_DELETE"
    page_edit = "PAGE_EDIT"
    page_manage_permissions = "PAGE_MANAGE_PERMISSIONS"
    page_view = "PAGE_VIEW"
    source_delete = "SOURCE_DELETE"
    source_manage = "SOURCE_MANAGE"
    source_view = "SOURCE_VIEW"
    ws_create_agents = "WS_CREATE_AGENTS"
    ws_create_collections = "WS_CREATE_COLLECTIONS"
    ws_create_groups = "WS_CREATE_GROUPS"
    ws_create_kts = "WS_CREATE_KTS"
    ws_create_pages = "WS_CREATE_PAGES"
    ws_create_sources = "WS_CREATE_SOURCES"
    ws_create_workspaces = "WS_CREATE_WORKSPACES"
    ws_manage_all_agents = "WS_MANAGE_ALL_AGENTS"
    ws_manage_all_collections = "WS_MANAGE_ALL_COLLECTIONS"
    ws_manage_all_groups = "WS_MANAGE_ALL_GROUPS"
    ws_manage_all_kts = "WS_MANAGE_ALL_KTS"
    ws_manage_all_pages = "WS_MANAGE_ALL_PAGES"
    ws_manage_all_sources = "WS_MANAGE_ALL_SOURCES"
    ws_manage_apps_ints = "WS_MANAGE_APPS_INTS"
    ws_manage_assist = "WS_MANAGE_ASSIST"
    ws_manage_billing = "WS_MANAGE_BILLING"
    ws_manage_hris = "WS_MANAGE_HRIS"
    ws_manage_sso = "WS_MANAGE_SSO"
    ws_manage_roles = "WS_MANAGE_ROLES"
    ws_manage_users = "WS_MANAGE_USERS"
    ws_manage_settings = "WS_MANAGE_SETTINGS"
    ws_view_analytics = "WS_VIEW_ANALYTICS"


class BulkOperationResponseItem(GuruModel):
    item_id: Annotated[str | None, Field(alias="itemId")] = None
    response_message: Annotated[str | None, Field(alias="responseMessage")] = None
    url: str | None = None
    status_code: Annotated[int | None, Field(alias="statusCode")] = None


class ShareStatus(Enum):
    private = "PRIVATE"
    team = "TEAM"
    public = "PUBLIC"


class VerificationType(Enum):
    absolute = "ABSOLUTE"
    relative = "RELATIVE"
    manual = "MANUAL"


class VerificationState(Enum):
    trusted = "TRUSTED"
    stale = "STALE"
    needs_verification = "NEEDS_VERIFICATION"
    synced_no_verification = "SYNCED_NO_VERIFICATION"
    none = "NONE"


class VerificationReason(Enum):
    update = "UPDATE"
    new_verifier = "NEW_VERIFIER"
    question = "QUESTION"
    requested = "REQUESTED"
    expired = "EXPIRED"
    automation = "AUTOMATION"


class LastVerificationModifiedByType(Enum):
    automation = "AUTOMATION"
    user = "USER"


class Type1(Enum):
    user = "user"
    user_group = "user-group"


class CardCollaborator(GuruModel):
    id: Annotated[
        str | None,
        Field(description="The ID (email address or group ID) of the collaborator"),
    ] = None
    date_created: Annotated[
        AwareDatetime | None,
        Field(
            alias="dateCreated",
            description="Date the collaborator was created",
            examples=[
                "Dates are in ISO-8601 format. Example date (January 2nd 2014 12pm UTC): 2014-01-02T12:00:00.000+0000"
            ],
        ),
    ] = None
    removed: bool | None = None
    type: Type1


class Status3(Enum):
    open = "OPEN"
    resolved = "RESOLVED"


class CardInfo(GuruModel):
    boards: list[dict[str, Any]] | None = None
    analytics: dict[str, int] | None = None
    members_with_card_view: Annotated[int | None, Field(alias="membersWithCardView")] = None
    members_without_card_view: Annotated[int | None, Field(alias="membersWithoutCardView")] = None


class ContentSyncType(Enum):
    zendesk = "ZENDESK"
    zendesk_import = "ZENDESK_IMPORT"
    confluence = "CONFLUENCE"
    manual = "MANUAL"
    google_drive = "GOOGLE_DRIVE"
    zenefits = "ZENEFITS"
    box = "BOX"
    kustomer = "KUSTOMER"
    dropbox = "DROPBOX"
    salesforce = "SALESFORCE"
    guru = "GURU"


class CardSyncInfo(GuruModel):
    content_sync_type: Annotated[ContentSyncType | None, Field(alias="contentSyncType")] = None
    last_sync_date: Annotated[AwareDatetime | None, Field(alias="lastSyncDate")] = None
    external_url: Annotated[str | None, Field(alias="externalUrl")] = None
    last_update_date: Annotated[AwareDatetime | None, Field(alias="lastUpdateDate")] = None


class Op2(Enum):
    eq = "EQ"
    notexists = "NOTEXISTS"


class CardVerifier(GuruModel):
    id: Annotated[str | None, Field(description="ID of the verifier")] = None
    date_created: Annotated[
        AwareDatetime | None,
        Field(
            alias="dateCreated",
            description="Date the verifier was created. Dates are in ISO-8601 format. Example date (January 2nd 2014 12pm UTC): 2014-01-02T12:00:00.000+0000",
        ),
    ] = None
    type: Type1


class Role(Enum):
    assistant = "ASSISTANT"
    user = "USER"
    system = "SYSTEM"


class ChatMode(Enum):
    chat = "CHAT"
    research = "RESEARCH"
    answer = "ANSWER"


class Type3(Enum):
    user = "USER"
    assistant_response = "ASSISTANT_RESPONSE"
    tool_call = "TOOL_CALL"
    agent_status = "AGENT_STATUS"
    interrupt = "INTERRUPT"
    diagnostics = "DIAGNOSTICS"


class AnswerMode(Enum):
    question = "QUESTION"
    slack_suggested_answer_question = "SLACK_SUGGESTED_ANSWER_QUESTION"
    preview = "PREVIEW"
    test_config = "TEST_CONFIG"


class Type4(Enum):
    answer = "ANSWER"
    approval = "APPROVAL"
    agent_status = "AGENT_STATUS"


class ChatMessageMetadata(GuruModel):
    type: Type4


class ChatThreadRequest(GuruModel):
    knowledge_agent_id: Annotated[str | None, Field(alias="knowledgeAgentId")] = None
    external_id: Annotated[str | None, Field(alias="externalId")] = None
    external_url: Annotated[str | None, Field(alias="externalUrl")] = None
    thread_type: Annotated[ThreadType | None, Field(alias="threadType")] = None


class CollectionFacet(GuruModel):
    id: str | None = None
    name: str | None = None
    count: int | None = None
    color: str | None = None


class SyncType(Enum):
    zendesk = "ZENDESK"
    zendesk_import = "ZENDESK_IMPORT"
    confluence = "CONFLUENCE"
    manual = "MANUAL"
    google_drive = "GOOGLE_DRIVE"
    zenefits = "ZENEFITS"
    box = "BOX"
    kustomer = "KUSTOMER"
    dropbox = "DROPBOX"
    salesforce = "SALESFORCE"
    guru = "GURU"


class CollectionType(Enum):
    internal = "INTERNAL"
    external = "EXTERNAL"


class CollectionTypeDetail(Enum):
    onboarding = "ONBOARDING"
    framework = "FRAMEWORK"
    user = "USER"
    external = "EXTERNAL"
    source = "SOURCE"
    welcome = "WELCOME"
    onboarding_unedited = "ONBOARDING_UNEDITED"


class DefaultVerificationType(Enum):
    absolute = "ABSOLUTE"
    relative = "RELATIVE"
    manual = "MANUAL"


class Op3(Enum):
    eq = "EQ"
    ne = "NE"


class Field1(Enum):
    verinterval = "VERINTERVAL"
    commentcount = "COMMENTCOUNT"
    favoritecount = "FAVORITECOUNT"
    boardcount = "BOARDCOUNT"
    unverifiedcopycount = "UNVERIFIEDCOPYCOUNT"
    unverifiedviewcount = "UNVERIFIEDVIEWCOUNT"
    tagcount = "TAGCOUNT"
    card_copied = "CARD_COPIED"
    card_viewed = "CARD_VIEWED"
    followcount = "FOLLOWCOUNT"


class Op4(Enum):
    eq = "EQ"
    ne = "NE"
    gt = "GT"
    gte = "GTE"
    lt = "LT"
    lte = "LTE"


class CustomFieldValueFacet(GuruModel):
    name: str | None = None
    value: str | None = None
    count: int | None = None


class DocumentType(Enum):
    guru = "GURU"
    source = "SOURCE"
    guru_attachment = "GURU_ATTACHMENT"
    web = "WEB"
    mcp = "MCP"


class DraftCommentReplySource(GuruModel):
    draft_id: Annotated[UUID | None, Field(alias="draftId")] = None
    draft_comment_id: Annotated[UUID | None, Field(alias="draftCommentId")] = None
    draft_comment_reply_id: Annotated[UUID | None, Field(alias="draftCommentReplyId")] = None


class DraftCommentSource(GuruModel):
    draft_id: Annotated[UUID | None, Field(alias="draftId")] = None
    draft_comment_id: Annotated[UUID | None, Field(alias="draftCommentId")] = None


class Event(GuruModel):
    properties: Annotated[
        dict[str, dict[str, Any]] | None,
        Field(description="Properties related to event"),
    ] = None
    id: Annotated[
        str | None,
        Field(
            description="Id of event. IDs are formatted like this: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
        ),
    ] = None
    type: str | None = None
    event_date: Annotated[
        AwareDatetime | None,
        Field(
            alias="eventDate",
            description="Timestamp of event. Dates are in ISO-8601 format. Example date (January 2nd 2014 12pm UTC): 2014-01-02T12:00:00.000+0000",
        ),
    ] = None
    event_type: Annotated[str | None, Field(alias="eventType", description="Event type")] = None
    user: Annotated[str | None, Field(description="Email of user")] = None


class Type5(Enum):
    tagcategory = "tagcategory"
    tag = "tag"
    absolute_date = "absolute-date"
    board_ids = "board-ids"
    folder_ids = "folder-ids"
    comment_from = "comment-from"
    count = "count"
    file_attachment = "file-attachment"
    file_type = "file-type"
    grouping = "grouping"
    group_verifier = "group-verifier"
    last_verified_by = "last-verified-by"
    last_modified_by = "last-modified-by"
    owner = "owner"
    original_owner = "originalOwner"
    pin = "pin"
    myfavorite = "myfavorite"
    myfollowedcards = "myfollowedcards"
    unverifiable = "unverifiable"
    top_performers = "topPerformers"
    most_popular_unverified = "mostPopularUnverified"
    mycards = "mycards"
    pin_url = "pin-url"
    relative_date = "relative-date"
    shared_to_user = "shared-to-user"
    title = "title"
    trust_state = "trust-state"
    share_type = "share-type"
    user_verifier = "user-verifier"
    recent_cards_viewed = "recentCardsViewed"
    card_template = "card-template"
    public_card = "public-card"
    verification_type = "verification-type"
    user_collaborator = "user-collaborator"
    group_collaborator = "group-collaborator"
    auto_archived = "auto-archived"
    myverifiedcards = "myverifiedcards"
    source_custom_field = "sourceCustomField"
    verification_modification_type = "verification-modification-type"
    object_type_id = "object-type-id"


class Expression(GuruModel):
    type: Type5


class Type6(Enum):
    slack = "slack"


class ExternalChatMessageContext(GuruModel):
    thread_type: Annotated[ThreadType | None, Field(alias="threadType")] = None
    type: Type6


class Type7(Enum):
    announcement = "announcement"


class ExtraDetailsModel(GuruModel):
    type: Type7


class FeaturedCard(GuruModel):
    card_id: Annotated[str | None, Field(alias="cardId")] = None
    image: str | None = None
    gradient: str | None = None


class Type8(Enum):
    image = "IMAGE"
    iframe = "IFRAME"
    video = "VIDEO"


class Op5(Enum):
    exists = "EXISTS"
    notexists = "NOTEXISTS"


class FileAttachmentExpression(Expression):
    op: Op5 | None = None


class Op6(Enum):
    eq = "EQ"
    ne = "NE"


class FileTypeExpression(Expression):
    value: str | None = None
    op: Op6 | None = None


class Op7(Enum):
    contains = "CONTAINS"
    notcontains = "NOTCONTAINS"
    containsimmediate = "CONTAINSIMMEDIATE"
    notcontainsimmediate = "NOTCONTAINSIMMEDIATE"


class FolderIdExpression(Expression):
    ids: list[str] | None = None
    op: Op7 | None = None


class Type9(Enum):
    card = "card"
    folder = "folder"


class FolderItem(GuruModel):
    id: str | None = None
    item_id: Annotated[str | None, Field(alias="itemId")] = None
    type: Type9


class GdDrive(GuruModel):
    id: str | None = None
    name: str | None = None


class GdFolder(GuruModel):
    id: str | None = None
    name: str | None = None


class Op8(Enum):
    eq = "EQ"


class GroupCollaboratorExpression(Expression):
    id: str | None = None
    op: Op8 | None = None


class Role1(Enum):
    admin = "ADMIN"
    author = "AUTHOR"
    member = "MEMBER"
    coll_admin = "COLL_ADMIN"


class Op9(Enum):
    eq = "EQ"
    ne = "NE"


class GroupVerifierExpression(Expression):
    op: Op9 | None = None
    group_id: Annotated[str | None, Field(alias="groupId")] = None


class Op10(Enum):
    and_ = "AND"
    or_ = "OR"


class GroupingExpression(Expression):
    op: Op10 | None = None
    nested_expressions: Annotated[list[Expression] | None, Field(alias="nestedExpressions")] = None


class ImageCropSpec(GuruModel):
    x: int | None = None
    y: int | None = None
    height: int | None = None
    width: int | None = None


class InternalProfileSlackDetail(GuruModel):
    slack_team_name: Annotated[str | None, Field(alias="slackTeamName")] = None
    slack_team_url: Annotated[str | None, Field(alias="slackTeamUrl")] = None


class JsonNode(GuruModel):
    pass


class WebSearchMode(Enum):
    disabled = "DISABLED"
    specific_sites = "SPECIFIC_SITES"
    entire_web = "ENTIRE_WEB"


class AgentType(Enum):
    deep_agent = "DEEP_AGENT"
    legacy = "LEGACY"


class Role2(Enum):
    admin = "ADMIN"
    expert = "EXPERT"
    viewer = "VIEWER"


class Model1(Enum):
    bedrock_sonnet_4_6 = "BEDROCK_SONNET_4_6"
    gpt_5_2 = "GPT_5_2"
    gpt_5_4 = "GPT_5_4"
    gpt_5_4_mini = "GPT_5_4_MINI"
    kimi_2_5 = "KIMI_2_5"


class KnowledgeAgentConfig(GuruModel):
    system_prompt: Annotated[str | None, Field(alias="systemPrompt")] = None
    model: Model1 | None = None


class VerificationFilterMode(Enum):
    all = "ALL"
    verified_only = "VERIFIED_ONLY"
    verified_and_none = "VERIFIED_AND_NONE"


class QualitySourceScope(Enum):
    all = "ALL"
    selected = "SELECTED"


class SkillType(Enum):
    general = "GENERAL"
    answer = "ANSWER"


class KnowledgeAgentSkill(GuruModel):
    id: UUID | None = None
    name: Annotated[
        str | None,
        Field(max_length=64, min_length=0, pattern="^[a-z0-9]([a-z0-9-]*[a-z0-9])?$"),
    ] = None
    description: Annotated[str | None, Field(max_length=1024, min_length=0)] = None
    content: str | None = None
    date_created: Annotated[AwareDatetime | None, Field(alias="dateCreated")] = None
    date_modified: Annotated[AwareDatetime | None, Field(alias="dateModified")] = None
    disabled: bool | None = None
    skill_type: Annotated[SkillType | None, Field(alias="skillType")] = None


class KnowledgeAgentSkillAccessRequest(GuruModel):
    group_id: Annotated[str | None, Field(alias="groupId")] = None


class KnowledgeAgentSkillFile(GuruModel):
    id: UUID | None = None
    full_path: Annotated[str | None, Field(alias="fullPath", max_length=1024, min_length=0)] = None
    content: str | None = None
    date_created: Annotated[AwareDatetime | None, Field(alias="dateCreated")] = None
    date_modified: Annotated[AwareDatetime | None, Field(alias="dateModified")] = None


class Platform(Enum):
    zendesk = "ZENDESK"
    liveperson = "LIVEPERSON"
    salesforce = "SALESFORCE"


class KnowledgeCenteredSupportInfo(GuruModel):
    card_id: Annotated[str | None, Field(alias="cardId")] = None
    conversation_id: Annotated[str | None, Field(alias="conversationId")] = None
    platform: Platform | None = None


class Op11(Enum):
    eq = "EQ"
    ne = "NE"


class LastModifiedByExpression(Expression):
    op: Op11 | None = None
    email: str | None = None


class LastVerifiedByExpression(Expression):
    op: Op11 | None = None
    email: str | None = None


class LinkedAccountIssue(GuruModel):
    id: str | None = None
    status: str | None = None
    error_description: Annotated[str | None, Field(alias="errorDescription")] = None
    error_details: Annotated[list[str] | None, Field(alias="errorDetails")] = None
    muted: bool | None = None
    first_incident_time: Annotated[AwareDatetime | None, Field(alias="firstIncidentTime")] = None
    last_incident_time: Annotated[AwareDatetime | None, Field(alias="lastIncidentTime")] = None
    user_email: Annotated[str | None, Field(alias="userEmail")] = None
    integration: str | None = None


class Decision(Enum):
    allow_once = "ALLOW_ONCE"
    always_allow = "ALWAYS_ALLOW"
    deny = "DENY"


class McpToolPermissionApproval(GuruModel):
    tool_name: Annotated[str | None, Field(alias="toolName")] = None
    decision: Decision
    connection_id: Annotated[str | None, Field(alias="connectionId")] = None
    approved: bool | None = None


class MentionSource(Enum):
    draft_comment = "DRAFT_COMMENT"
    draft_comment_reply = "DRAFT_COMMENT_REPLY"


class Action(Enum):
    feedback = "FEEDBACK"
    assign_expert = "ASSIGN_EXPERT"
    approval = "APPROVAL"
    reject = "REJECT"


class MessageActionRequest(GuruModel):
    action: Action | None = None
    data: JsonNode | None = None


class MgDrive(GuruModel):
    id: str | None = None
    name: str | None = None


class MgFolder(GuruModel):
    id: str | None = None
    name: str | None = None


class MostPopularUnverifiedExpression(Expression):
    pass


class MyCardsExpression(Expression):
    pass


class MyFavoriteExpression(Expression):
    pass


class MyFollowedCardsExpression(Expression):
    pass


class MyVerifiedCardsExpression(Expression):
    pass


class ObjectType1(Enum):
    agent = "AGENT"
    page = "PAGE"
    collection = "COLLECTION"


class Scope(Enum):
    workspace = "WORKSPACE"
    user = "USER"


class NavigationPinRequest(GuruModel):
    object_type: Annotated[ObjectType1 | None, Field(alias="objectType")] = None
    object_id: Annotated[UUID | None, Field(alias="objectId")] = None
    previous_pin_id: Annotated[UUID | None, Field(alias="previousPinId")] = None


class Number(GuruModel):
    pass


class State(Enum):
    org = "ORG"
    global_ = "GLOBAL"


class OAuthClient(GuruModel):
    client_id: Annotated[str | None, Field(alias="clientId")] = None
    client_secret: Annotated[str | None, Field(alias="clientSecret")] = None
    redirect_uris: Annotated[list[str] | None, Field(alias="redirectUris")] = None
    scopes: list[str] | None = None
    name: str | None = None
    logo_url: Annotated[str | None, Field(alias="logoUrl")] = None
    description: str | None = None
    bottom_description: Annotated[str | None, Field(alias="bottomDescription")] = None
    configuration: str | None = None
    state: State | None = None


class Type10(Enum):
    field = "FIELD"
    tag = "TAG"
    template = "TEMPLATE"


class TargetType(Enum):
    created_date = "CREATED_DATE"
    modified_date = "MODIFIED_DATE"
    custom = "CUSTOM"


class OverrideDataType(Enum):
    json = "JSON"
    text = "TEXT"
    html = "HTML"
    markdown = "MARKDOWN"
    mixed_html_markdown = "MIXED_HTML_MARKDOWN"
    long = "LONG"
    double = "DOUBLE"
    boolean = "BOOLEAN"
    date_time = "DATE_TIME"


class DataType(Enum):
    json = "JSON"
    text = "TEXT"
    html = "HTML"
    markdown = "MARKDOWN"
    mixed_html_markdown = "MIXED_HTML_MARKDOWN"
    long = "LONG"
    double = "DOUBLE"
    boolean = "BOOLEAN"
    date_time = "DATE_TIME"


class ObjectField(GuruModel):
    name: str | None = None
    id: str | None = None
    external_id: Annotated[str | None, Field(alias="externalId")] = None
    data_type: Annotated[DataType | None, Field(alias="dataType")] = None
    content_selector: Annotated[str | None, Field(alias="contentSelector")] = None


class Type11(Enum):
    hierarchical = "HIERARCHICAL"
    simple = "SIMPLE"


class ObjectTagConfig(GuruModel):
    id: str | None = None
    type: Type11 | None = None
    name: str | None = None
    allow_multiple_values: Annotated[bool | None, Field(alias="allowMultipleValues")] = None
    data_type: Annotated[DataType | None, Field(alias="dataType")] = None
    external_id: Annotated[str | None, Field(alias="externalId")] = None
    current_sync_number: Annotated[int | None, Field(alias="currentSyncNumber")] = None


class SourceDataType(Enum):
    record = "RECORD"
    structured = "STRUCTURED"


class Op13(Enum):
    eq = "EQ"


class ObjectTypeIdExpression(Expression):
    id: str | None = None
    op: Op13 | None = None


class ExternalUrlTemplateType(Enum):
    simple = "SIMPLE"
    freemarker = "FREEMARKER"


class TitleTemplateType(Enum):
    simple = "SIMPLE"
    freemarker = "FREEMARKER"


class OrderByTemplateType(Enum):
    simple = "SIMPLE"
    freemarker = "FREEMARKER"


class OrderByOrderType(Enum):
    asc = "ASC"
    desc = "DESC"


class Op14(Enum):
    eq = "EQ"
    ne = "NE"


class OriginalOwnerExpression(Expression):
    op: Op14 | None = None
    email: str | None = None


class OwnerExpression(Expression):
    op: Op14 | None = None
    email: str | None = None


class Status4(Enum):
    active = "ACTIVE"
    pending = "PENDING"


class Op16(Enum):
    exists = "EXISTS"
    notexists = "NOTEXISTS"


class PinExpression(Expression):
    op: Op16 | None = None


class PinMetadata(GuruModel):
    emoji: str | None = None
    color: str | None = None
    badge_emoji: Annotated[str | None, Field(alias="badgeEmoji")] = None
    image_url: Annotated[str | None, Field(alias="imageUrl")] = None
    is_home_page: Annotated[bool | None, Field(alias="isHomePage")] = None


class PinUrlContainsExpression(Expression):
    value: str | None = None


class PinnableObjectModel(GuruModel):
    id: UUID | None = None
    object_type: Annotated[ObjectType1 | None, Field(alias="objectType")] = None
    name: str | None = None
    description: str | None = None
    metadata: PinMetadata | None = None


class PresetKey(Enum):
    slack = "SLACK"


class PresetSetupConfig(GuruModel):
    preset_key: Annotated[PresetKey | None, Field(alias="presetKey")] = None


class PromptTestParams(GuruModel):
    tone: str | None = None
    answer_prompt: Annotated[str | None, Field(alias="answerPrompt")] = None


class Op17(Enum):
    ispublic = "ISPUBLIC"
    isnotpublic = "ISNOTPUBLIC"


class PublicCardExpression(Expression):
    op: Op17 | None = None


class Mode(Enum):
    verify = "VERIFY"
    unverify = "UNVERIFY"
    archive = "ARCHIVE"


class Action1(Enum):
    verify = "VERIFY"
    unverify = "UNVERIFY"
    error = "ERROR"
    skipped = "SKIPPED"
    insufficient_info = "INSUFFICIENT_INFO"


class QualityAgentSimulation(GuruModel):
    agent_id: Annotated[
        str,
        Field(alias="agentId", description="The ID of the Knowledge Agent to simulate."),
    ]
    mode: Annotated[Mode, Field(description="The quality mode to use for the simulation.")]


class QualityAgentSimulationResponse(GuruModel):
    run_id: Annotated[
        str | None,
        Field(alias="runId", description="The run ID for the simulated quality agent run."),
    ] = None


class QualityRule(GuruModel):
    rule: str | None = None
    ignore_lva_override: Annotated[bool | None, Field(alias="ignoreLvaOverride")] = None


class QueryType(Enum):
    cards = "cards"
    archived = "archived"
    draft = "draft"
    legacy = "legacy"
    search_cards = "search_cards"


class ReactionDetail(GuruModel):
    count: int | None = None
    shortcode: str | None = None
    first_reaction_at: Annotated[AwareDatetime | None, Field(alias="firstReactionAt")] = None
    current_user_reaction_id: Annotated[str | None, Field(alias="currentUserReactionId")] = None


class RecentCardsViewedExpression(Expression):
    days_ago: Annotated[int | None, Field(alias="daysAgo")] = None


class Type12(Enum):
    one_to_one = "ONE_TO_ONE"
    one_to_many = "ONE_TO_MANY"
    many_to_one = "MANY_TO_ONE"
    many_to_many = "MANY_TO_MANY"


class MappedBy(Enum):
    source = "SOURCE"
    target = "TARGET"


class SourceMetaField(Enum):
    object_type = "OBJECT_TYPE"
    external_id = "EXTERNAL_ID"
    external_url = "EXTERNAL_URL"
    title = "TITLE"
    json_content = "JSON_CONTENT"
    content = "CONTENT"


class TargetMetaField(Enum):
    object_type = "OBJECT_TYPE"
    external_id = "EXTERNAL_ID"
    external_url = "EXTERNAL_URL"
    title = "TITLE"
    json_content = "JSON_CONTENT"
    content = "CONTENT"


class Field2(Enum):
    datecreated = "DATECREATED"
    nextverification = "NEXTVERIFICATION"
    lastverified = "LASTVERIFIED"
    lastmodified = "LASTMODIFIED"
    first_comment_created_event = "FIRST_COMMENT_CREATED_EVENT"
    last_comment_created_event = "LAST_COMMENT_CREATED_EVENT"
    first_card_copied_event = "FIRST_CARD_COPIED_EVENT"
    last_card_copied_event = "LAST_CARD_COPIED_EVENT"
    last_card_viewed_event = "LAST_CARD_VIEWED_EVENT"
    first_card_viewed_event = "FIRST_CARD_VIEWED_EVENT"


class Op18(Enum):
    gt = "GT"
    gte = "GTE"
    lt = "LT"
    lte = "LTE"


class RelativeDateExpression(Expression):
    days_from_now: Annotated[int | None, Field(alias="daysFromNow")] = None
    days_ago: Annotated[int | None, Field(alias="daysAgo")] = None
    field: Field2 | None = None
    op: Op18 | None = None


class RemoteSourceObjectSync(GuruModel):
    name: str | None = None
    last_synced_date: Annotated[AwareDatetime | None, Field(alias="lastSyncedDate")] = None
    last_sync_attempt: Annotated[AwareDatetime | None, Field(alias="lastSyncAttempt")] = None
    last_sync_completed: Annotated[AwareDatetime | None, Field(alias="lastSyncCompleted")] = None
    sync_status: Annotated[str | None, Field(alias="syncStatus")] = None
    last_sync_status: Annotated[str | None, Field(alias="lastSyncStatus")] = None


class RoleType(Enum):
    user = "USER"
    system = "SYSTEM"


class SystemRole(Enum):
    admin = "ADMIN"
    creator = "CREATOR"
    owner = "OWNER"
    viewer = "VIEWER"
    editor = "EDITOR"


class RoleModel(GuruModel):
    id: UUID | None = None
    name: str | None = None
    permissions: list[Permission] | None = None
    role_type: Annotated[RoleType | None, Field(alias="roleType")] = None
    system_role: Annotated[SystemRole | None, Field(alias="systemRole")] = None


class ScheduleArchivalRequest(GuruModel):
    scheduled_archive_date: Annotated[
        AwareDatetime,
        Field(
            alias="scheduledArchiveDate",
            description="The date when the card should be archived",
            examples=[
                "Dates are in ISO-8601 format. Example date (January 2nd 2014 12pm UTC): 2014-01-02T12:00:00.000+0000"
            ],
        ),
    ]


class ServerSentEvent(GuruModel):
    pass


class Op19(Enum):
    eq = "EQ"
    ne = "NE"


class ShareType(Enum):
    private = "PRIVATE"
    team = "TEAM"
    public = "PUBLIC"


class ShareTypeExpression(Expression):
    op: Op19 | None = None
    share_type: Annotated[ShareType | None, Field(alias="shareType")] = None


class SharedToUserExpression(Expression):
    email: str | None = None


class SimpleApprovalAction(GuruModel):
    approved: bool | None = None


class SlackChannel(GuruModel):
    name: str | None = None
    id: str | None = None
    private: bool | None = None
    members: list[str] | None = None
    is_archived: bool | None = None


class SlackThreadMessageContext(ExternalChatMessageContext):
    slack_team_id: Annotated[str | None, Field(alias="slackTeamId")] = None
    channel_id: Annotated[str | None, Field(alias="channelId")] = None
    thread_ts: Annotated[str | None, Field(alias="threadTs")] = None
    passive_mode: Annotated[bool | None, Field(alias="passiveMode")] = None
    message_ts: Annotated[str | None, Field(alias="messageTs")] = None
    is_dm: Annotated[bool | None, Field(alias="isDM")] = None


class Type13(Enum):
    last_modified = "lastModified"
    last_modified_by = "lastModifiedBy"
    board_count = "boardCount"
    verification_state = "verificationState"
    copy_count = "copyCount"
    view_count = "viewCount"
    favorite_count = "favoriteCount"
    follower_count = "followerCount"
    date_created = "dateCreated"
    verification_interval = "verificationInterval"
    verifier = "verifier"
    owner = "owner"
    original_owner = "originalOwner"
    last_verified_by = "lastVerifiedBy"
    last_verified = "lastVerified"
    verification_reason = "verificationReason"
    popularity = "popularity"
    unverified_views_copies = "unverifiedViewsCopies"
    next_verification_date = "nextVerificationDate"
    collection = "collection"
    title = "title"
    followed_date = "followedDate"
    pending_auto_archive = "pendingAutoArchive"
    relevancy = "relevancy"
    verification_state_1 = "verification_state"
    last_ver_action_date = "last_ver_action_date"
    last_ver_action_type = "last_ver_action_type"


class Dir(Enum):
    asc = "ASC"
    desc = "DESC"


class Sort(GuruModel):
    type: Type13 | None = None
    dir: Dir | None = None


class SyncStatus(Enum):
    syncing = "SYNCING"
    synced = "SYNCED"
    failed = "FAILED"
    invalid = "INVALID"


class StatusReason(Enum):
    invalid_authentication = "INVALID_AUTHENTICATION"
    unauthorized = "UNAUTHORIZED"
    no_api_access = "NO_API_ACCESS"
    target_inaccessible = "TARGET_INACCESSIBLE"
    too_large = "TOO_LARGE"
    target_insecure = "TARGET_INSECURE"
    auth_expired = "AUTH_EXPIRED"
    missing_feature = "MISSING_FEATURE"
    api_error = "API_ERROR"
    no_admin = "NO_ADMIN"
    api_timeout = "API_TIMEOUT"
    api_interrupted = "API_INTERRUPTED"
    parsing_error = "PARSING_ERROR"
    extraction_error = "EXTRACTION_ERROR"
    homeboard_import_failed = "HOMEBOARD_IMPORT_FAILED"
    job_timeout = "JOB_TIMEOUT"
    unknown_error = "UNKNOWN_ERROR"


class Type14(Enum):
    google_drive = "GOOGLE_DRIVE"
    google_drive_v2 = "GOOGLE_DRIVE_V2"
    slack = "SLACK"
    custom = "CUSTOM"
    guru_ipaas = "GURU_IPAAS"
    gsheet = "GSHEET"
    merge_file = "MERGE_FILE"
    merge_ticket = "MERGE_TICKET"
    merge_crm = "MERGE_CRM"
    file_upload = "FILE_UPLOAD"
    knowledge_agent_files = "KNOWLEDGE_AGENT_FILES"
    sample = "SAMPLE"


class SourceConfig(GuruModel):
    type: Type14


class Op20(Enum):
    equals = "EQUALS"
    not_equals = "NOT_EQUALS"
    less_than = "LESS_THAN"
    less_than_or_equal = "LESS_THAN_OR_EQUAL"
    greater_than = "GREATER_THAN"
    greater_than_or_equal = "GREATER_THAN_OR_EQUAL"
    in_ = "IN"
    contains = "CONTAINS"
    lt_days_from_now = "LT_DAYS_FROM_NOW"
    gt_days_from_now = "GT_DAYS_FROM_NOW"
    lte_days_from_now = "LTE_DAYS_FROM_NOW"
    gte_days_from_now = "GTE_DAYS_FROM_NOW"


class SourceCustomFieldExpression(Expression):
    op: Op20 | None = None
    field_id: Annotated[str | None, Field(alias="fieldId")] = None
    field_value: Annotated[str | None, Field(alias="fieldValue")] = None


class ConfigType(Enum):
    google_drive = "GOOGLE_DRIVE"
    google_drive_v2 = "GOOGLE_DRIVE_V2"
    slack = "SLACK"
    custom = "CUSTOM"
    guru_ipaas = "GURU_IPAAS"
    gsheet = "GSHEET"
    merge_file = "MERGE_FILE"
    merge_ticket = "MERGE_TICKET"
    merge_crm = "MERGE_CRM"
    file_upload = "FILE_UPLOAD"
    knowledge_agent_files = "KNOWLEDGE_AGENT_FILES"
    sample = "SAMPLE"


class Availability(Enum):
    none = "NONE"
    general = "GENERAL"
    team = "TEAM"


class CustomDataStrategy(Enum):
    remote_data = "REMOTE_DATA"
    remote_fields = "REMOTE_FIELDS"


class SourceDefinitionConfig(GuruModel):
    discriminator_type: Annotated[str | None, Field(alias="discriminatorType")] = None
    merge_dev_integration_name: Annotated[str | None, Field(alias="mergeDevIntegrationName")] = None
    ipaas_integration_id: Annotated[str | None, Field(alias="ipaasIntegrationId")] = None
    use_source_name_for_facet: Annotated[bool | None, Field(alias="useSourceNameForFacet")] = None
    model_names: Annotated[dict[str, str] | None, Field(alias="modelNames")] = None
    custom_data_strategy: Annotated[
        CustomDataStrategy | None, Field(alias="customDataStrategy")
    ] = None
    supports_source_native_permissions: Annotated[
        bool | None, Field(alias="supportsSourceNativePermissions")
    ] = None
    source_native_permissions_require_admin: Annotated[
        bool | None, Field(alias="sourceNativePermissionsRequireAdmin")
    ] = None
    enable_ocr: Annotated[bool | None, Field(alias="enableOcr")] = None


class SourceFilter(GuruModel):
    object_type_id: Annotated[str | None, Field(alias="objectTypeId")] = None
    filter_query: Annotated[Expression | None, Field(alias="filterQuery")] = None


class LastSyncStatus(Enum):
    syncing = "SYNCING"
    synced = "SYNCED"
    failed = "FAILED"
    invalid = "INVALID"


class LastStatusReason(Enum):
    invalid_authentication = "INVALID_AUTHENTICATION"
    unauthorized = "UNAUTHORIZED"
    no_api_access = "NO_API_ACCESS"
    target_inaccessible = "TARGET_INACCESSIBLE"
    too_large = "TOO_LARGE"
    target_insecure = "TARGET_INSECURE"
    auth_expired = "AUTH_EXPIRED"
    missing_feature = "MISSING_FEATURE"
    api_error = "API_ERROR"
    no_admin = "NO_ADMIN"
    api_timeout = "API_TIMEOUT"
    api_interrupted = "API_INTERRUPTED"
    parsing_error = "PARSING_ERROR"
    extraction_error = "EXTRACTION_ERROR"
    homeboard_import_failed = "HOMEBOARD_IMPORT_FAILED"
    job_timeout = "JOB_TIMEOUT"
    unknown_error = "UNKNOWN_ERROR"


class SourceTypeFacet(GuruModel):
    id: str | None = None
    name: str | None = None
    type: str | None = None
    icon_url: Annotated[str | None, Field(alias="iconUrl")] = None
    count: int | None = None


class Type15(Enum):
    team_card_count = "team-card-count"
    team_trust_score = "team-trust-score"
    collection_trust_score = "collection-trust-score"
    card_count = "card-count"


class Stats(GuruModel):
    type: Type15


class SuggestedQuestions(GuruModel):
    questions: list[str] | None = None


class Tag(GuruModel):
    value: Annotated[str | None, Field(description="The name of the Tag")] = None
    id: Annotated[
        str | None,
        Field(
            description="The ID of the Tag",
            examples=["IDs are formatted like this: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"],
        ),
    ] = None
    number_of_cards: Annotated[
        int | None,
        Field(
            alias="numberOfCards",
            description="The number of cards associated with this Tag",
        ),
    ] = None
    category_id: Annotated[
        str | None,
        Field(
            alias="categoryId",
            description="If the tag belongs to a category, this is the ID for the category",
            examples=["IDs are formatted like this: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"],
        ),
    ] = None
    category_name: Annotated[
        str | None,
        Field(
            alias="categoryName",
            description="If the tag belongs to a category, this is the name for the category",
        ),
    ] = None


class Op21(Enum):
    exists = "EXISTS"
    notexists = "NOTEXISTS"


class TagCategoryExistsExpression(Expression):
    ids: list[str] | None = None
    op: Op21 | None = None


class TagExistsExpression(Expression):
    ids: list[str] | None = None
    op: Op21 | None = None


class TagFacet(GuruModel):
    id: str | None = None
    name: str | None = None
    count: int | None = None


class DefaultUserType(Enum):
    free_core = "FREE_CORE"
    core = "CORE"


class Status5(Enum):
    active = "ACTIVE"
    dormant = "DORMANT"
    locked = "LOCKED"
    expired = "EXPIRED"
    locked_pay = "LOCKED_PAY"


class TeamCardCount(Stats):
    count: int | None = None


class TeamDomain(GuruModel):
    verification_code: Annotated[str | None, Field(alias="verificationCode")] = None
    verified: bool | None = None
    capture: bool | None = None
    domain: str | None = None


class TeamEdition(GuruModel):
    admin_overrides: Annotated[dict[str, str] | None, Field(alias="adminOverrides")] = None
    name: str | None = None
    key: str | None = None
    id: str | None = None
    features: dict[str, str] | None = None
    code: str | None = None
    usage: dict[str, int] | None = None


class Status6(Enum):
    valid = "VALID"
    invalid = "INVALID"


class SetupMode(Enum):
    oauth_dcr = "OAUTH_DCR"
    preset = "PRESET"


class TeamExternalMcpServer(GuruModel):
    id: str | None = None
    url: str | None = None
    display_name: Annotated[str | None, Field(alias="displayName")] = None
    description: str | None = None
    icon_url: Annotated[str | None, Field(alias="iconUrl")] = None
    status: Status6 | None = None
    setup_mode: Annotated[SetupMode | None, Field(alias="setupMode")] = None
    setup_config: Annotated[PresetSetupConfig | None, Field(alias="setupConfig")] = None
    date_created: Annotated[AwareDatetime | None, Field(alias="dateCreated")] = None


class TeamTrustScore(Stats):
    trusted_count: Annotated[int | None, Field(alias="trustedCount")] = None
    needs_verification_count: Annotated[int | None, Field(alias="needsVerificationCount")] = None


class HighestRole(Enum):
    admin = "ADMIN"
    author = "AUTHOR"
    member = "MEMBER"
    coll_admin = "COLL_ADMIN"


class Op23(Enum):
    is_ = "IS"
    contains = "CONTAINS"
    notcontains = "NOTCONTAINS"
    startswith = "STARTSWITH"
    endswith = "ENDSWITH"


class TitleExpression(Expression):
    value: str | None = None
    op: Op23 | None = None


class TokenUsage(GuruModel):
    prompt_tokens: Annotated[int | None, Field(alias="promptTokens")] = None
    completion_tokens: Annotated[int | None, Field(alias="completionTokens")] = None
    total_tokens: Annotated[int | None, Field(alias="totalTokens")] = None
    model: str | None = None
    activity_name: Annotated[str | None, Field(alias="activityName")] = None


class TopPerformersExpression(Expression):
    pass


class Op24(Enum):
    eq = "EQ"
    ne = "NE"


class TrustStateExpression(Expression):
    verification_state: Annotated[VerificationState | None, Field(alias="verificationState")] = None
    op: Op24 | None = None


class UnverifiableCardExpression(Expression):
    pass


class UseCase(GuruModel):
    description: Annotated[str | None, Field(description="A description of this use case")] = None


class Status7(Enum):
    active = "ACTIVE"
    pending = "PENDING"


class Op25(Enum):
    eq = "EQ"


class UserCollaboratorExpression(Expression):
    id: str | None = None
    op: Op25 | None = None


class Type16(Enum):
    knowledge_agent = "knowledge-agent"


class UserExtendedInfo(GuruModel):
    type: Type16


class Status8(Enum):
    valid = "VALID"
    invalid = "INVALID"


class UserExternalMcpConnection(GuruModel):
    id: str | None = None
    mcp_server: Annotated[TeamExternalMcpServer | None, Field(alias="mcpServer")] = None
    token_expires_at: Annotated[AwareDatetime | None, Field(alias="tokenExpiresAt")] = None
    status: Status8 | None = None
    connected_at: Annotated[AwareDatetime | None, Field(alias="connectedAt")] = None


class Role3(Enum):
    admin = "ADMIN"
    author = "AUTHOR"
    member = "MEMBER"
    coll_admin = "COLL_ADMIN"


class Role4(Enum):
    author = "AUTHOR"
    member = "MEMBER"
    coll_admin = "COLL_ADMIN"


class UserProfile(GuruModel):
    role_level: Annotated[
        str | None,
        Field(
            alias="roleLevel",
            description="The level at which the user operates in their current role",
        ),
    ] = None
    use_case_list: Annotated[
        list[UseCase] | None,
        Field(
            alias="useCaseList",
            description="Describes different ways the user intends to use Guru",
        ),
    ] = None
    role: Annotated[
        str | None,
        Field(description="The functional role a Guru user performs on their team"),
    ] = None


class Op26(Enum):
    eq = "EQ"
    ne = "NE"


class UserVerifierExpression(Expression):
    op: Op26 | None = None
    email: str | None = None


class Op27(Enum):
    eq = "EQ"


class VerificationModificationType(Enum):
    automation = "AUTOMATION"
    user = "USER"


class VerificationModificationTypeExpression(Expression):
    op: Op27 | None = None
    verification_modification_type: Annotated[
        VerificationModificationType | None, Field(alias="verificationModificationType")
    ] = None


class VerificationTypeExpression(Expression):
    verification_type: Annotated[VerificationType | None, Field(alias="verificationType")] = None


class WebSearchSite(GuruModel):
    description: str | None = None
    site: str | None = None


class TokenType(Enum):
    api = "API"
    session = "SESSION"
    collection = "COLLECTION"
    other = "OTHER"
    unknown = "UNKNOWN"


class Type17(Enum):
    featured_cards = "FEATURED_CARDS"
    featured_cards_v2 = "FEATURED_CARDS_V2"
    content = "CONTENT"
    announcements = "ANNOUNCEMENTS"
    recommended_for_you = "RECOMMENDED_FOR_YOU"
    image = "IMAGE"


class Widget(GuruModel):
    id: str | None = None
    type: Type17
    visible: bool | None = None
    date_created: Annotated[AwareDatetime | None, Field(alias="dateCreated")] = None
    date_last_updated: Annotated[AwareDatetime | None, Field(alias="dateLastUpdated")] = None
    last_updated_by: Annotated[str | None, Field(alias="lastUpdatedBy")] = None


class AbsoluteDateExpression(Expression):
    value: AwareDatetime | None = None
    field: FieldModel | None = None
    op: Op | None = None


class AgentQuestionResponse(AgentResponse):
    pass


class AgentStatusMetadata(ChatMessageMetadata):
    rejected: bool | None = None


class AnalyticsSummary(GuruModel):
    events_by_type: Annotated[dict[str, Number] | None, Field(alias="eventsByType")] = None


class AnnouncementExtraDetails(ExtraDetailsModel):
    announcement_id: Annotated[UUID | None, Field(alias="announcementId")] = None


class AnnouncementUser(GuruModel):
    announcement_read_at: Annotated[AwareDatetime | None, Field(alias="announcementReadAt")] = None
    announcement_viewed_at: Annotated[AwareDatetime | None, Field(alias="announcementViewedAt")] = (
        None
    )
    id: Annotated[str | None, Field(description="The identifier of this User")] = None
    user_profile: Annotated[
        UserProfile | None,
        Field(alias="userProfile", description="Additional information about a user"),
    ] = None
    last_name: Annotated[
        str | None, Field(alias="lastName", description="The user's last name")
    ] = None
    first_name: Annotated[
        str | None, Field(alias="firstName", description="The user's first name")
    ] = None
    profile_pic_url: Annotated[
        str | None,
        Field(alias="profilePicUrl", description="The profile picture url for the user"),
    ] = None
    joined_date: Annotated[AwareDatetime | None, Field(alias="joinedDate")] = None
    extended_info: Annotated[UserExtendedInfo | None, Field(alias="extendedInfo")] = None
    user_type: Annotated[UserType | None, Field(alias="userType")] = None
    status: Annotated[
        Status | None,
        Field(
            description="The status of a User can be ACTIVE or PENDING. The User must verify their email address to be considered ACTIVE."
        ),
    ] = None
    email: Annotated[str, Field(description="The user's email address")]


class AnnouncementsWidget(Widget):
    pass


class AnswerAssignment(GuruModel):
    assignee: CardVerifier | None = None
    note: str | None = None


class AnswerMetadata(ChatMessageMetadata):
    answer_id: Annotated[str | None, Field(alias="answerId")] = None
    feedback: Feedback | None = None
    assignee: CardVerifier | None = None


class AnswerQuerySpec(GuruModel):
    question: str | None = None
    agent_id: Annotated[str | None, Field(alias="agentId")] = None
    minimal_answer_only: Annotated[bool | None, Field(alias="minimalAnswerOnly")] = None
    bypass_question_detection: Annotated[bool | None, Field(alias="bypassQuestionDetection")] = None
    context: ExternalChatMessageContext | None = None
    thread_type: Annotated[ThreadType | None, Field(alias="threadType")] = None


class ApprovalMetadata(ChatMessageMetadata):
    approved: bool | None = None


class AutoArchivedExpression(Expression):
    op: Op1 | None = None


class BulkOperationResponse(GuruModel):
    id: str | None = None
    response_message: Annotated[str | None, Field(alias="responseMessage")] = None
    status_code: Annotated[int | None, Field(alias="statusCode")] = None
    items: list[BulkOperationResponseItem] | None = None


class CardTemplateExpression(Expression):
    value: str | None = None
    op: Op2 | None = None


class CollectionCardCount(Stats):
    count: int | None = None


class CollectionFilter(GuruModel):
    filter_query: Annotated[Expression | None, Field(alias="filterQuery")] = None


class CollectionTrustScore(Stats):
    trusted_count: Annotated[int | None, Field(alias="trustedCount")] = None
    needs_verification_count: Annotated[int | None, Field(alias="needsVerificationCount")] = None


class CommentFromExpression(Expression):
    op: Op3 | None = None
    email: str | None = None


class ContentWidget(Widget):
    message: str | None = None
    title: str | None = None


class CountExpression(Expression):
    value: int | None = None
    field: Field1 | None = None
    op: Op4 | None = None


class CustomFieldFacet(GuruModel):
    id: str | None = None
    field_name: Annotated[str | None, Field(alias="fieldName")] = None
    hierarchical: bool | None = None
    values: list[CustomFieldValueFacet] | None = None


class DataMaskConfig(GuruModel):
    id: str | None = None
    field: ObjectField | None = None
    match_pattern: Annotated[str | None, Field(alias="matchPattern")] = None
    match_replacement: Annotated[str | None, Field(alias="matchReplacement")] = None


class FeaturedCardsWidget(Widget):
    cards: list[str] | None = None


class FeaturedCardsWidgetV2(Widget):
    featured_cards: Annotated[list[FeaturedCard] | None, Field(alias="featuredCards")] = None


class FeaturedImageCandidateEntry(GuruModel):
    id: str | None = None
    type: Type8 | None = None
    crop_spec: Annotated[ImageCropSpec | None, Field(alias="cropSpec")] = None
    signed_url: Annotated[str | None, Field(alias="signedUrl")] = None
    url: str | None = None
    height: int | None = None
    width: int | None = None


class FileUploadSourceConfig(SourceConfig):
    name: str | None = None
    description: str | None = None


class GSheetSourceConfig(SourceConfig):
    document_url: Annotated[str | None, Field(alias="documentUrl")] = None
    name: str | None = None
    description: str | None = None
    icon_url: Annotated[str | None, Field(alias="iconUrl")] = None
    object_name: Annotated[str | None, Field(alias="objectName")] = None
    header_row: Annotated[int | None, Field(alias="headerRow")] = None
    id_column: Annotated[str | None, Field(alias="idColumn")] = None
    title_column: Annotated[str | None, Field(alias="titleColumn")] = None
    url_column: Annotated[str | None, Field(alias="urlColumn")] = None
    icon_data: Annotated[str | None, Field(alias="iconData")] = None
    icon_media_type: Annotated[str | None, Field(alias="iconMediaType")] = None
    document_id: Annotated[str | None, Field(alias="documentId")] = None
    sheet_id: Annotated[int | None, Field(alias="sheetId")] = None


class GldObjectTypeFacet(GuruModel):
    id: str | None = None
    name: str | None = None
    count: int | None = None
    custom_fields: Annotated[list[CustomFieldFacet] | None, Field(alias="customFields")] = None


class GoogleDriveSourceConfig(SourceConfig):
    folder_id: Annotated[str | None, Field(alias="folderId")] = None
    folder_name: Annotated[str | None, Field(alias="folderName")] = None
    description: str | None = None


class GoogleDriveV2SourceConfig(SourceConfig):
    folder_id: Annotated[str | None, Field(alias="folderId")] = None
    folder_name: Annotated[str | None, Field(alias="folderName")] = None
    honor_allow_file_discovery: Annotated[bool | None, Field(alias="honorAllowFileDiscovery")] = (
        None
    )
    description: str | None = None
    folders: list[GdFolder] | None = None
    drives: list[GdDrive] | None = None
    absolute_modifed_date_filter: Annotated[
        AwareDatetime | None, Field(alias="absoluteModifedDateFilter")
    ] = None
    relative_modified_date_filter_seconds: Annotated[
        int | None, Field(alias="relativeModifiedDateFilterSeconds")
    ] = None


class ImageWidget(Widget):
    main_image: Annotated[str | None, Field(alias="mainImage")] = None


class KnowledgeAgentExternalMcpServer(GuruModel):
    mcp_server: Annotated[TeamExternalMcpServer | None, Field(alias="mcpServer")] = None
    is_required: Annotated[bool | None, Field(alias="isRequired")] = None
    date_created: Annotated[AwareDatetime | None, Field(alias="dateCreated")] = None


class KnowledgeAgentFilesSourceConfig(SourceConfig):
    name: str | None = None
    icon_url: Annotated[str | None, Field(alias="iconUrl")] = None


class KnowledgeAgentFilterConfig(GuruModel):
    source_filters: Annotated[
        dict[str, list[SourceFilter]] | None, Field(alias="sourceFilters")
    ] = None
    collection_filters: Annotated[
        dict[str, CollectionFilter] | None, Field(alias="collectionFilters")
    ] = None


class KnowledgeAgentMcpStatus(GuruModel):
    mcp_server: Annotated[TeamExternalMcpServer | None, Field(alias="mcpServer")] = None
    is_required: Annotated[bool | None, Field(alias="isRequired")] = None
    is_connected: Annotated[bool | None, Field(alias="isConnected")] = None
    connection: UserExternalMcpConnection | None = None


class KnowledgeAgentSetup(GuruModel):
    system_prompt: Annotated[str | None, Field(alias="systemPrompt")] = None
    skill_files: Annotated[list[KnowledgeAgentSkillFile] | None, Field(alias="skillFiles")] = None
    model_provider: Annotated[str | None, Field(alias="modelProvider")] = None
    model_identifier: Annotated[str | None, Field(alias="modelIdentifier")] = None
    model_max_output_tokens: Annotated[int | None, Field(alias="modelMaxOutputTokens")] = None
    model_max_input_tokens: Annotated[int | None, Field(alias="modelMaxInputTokens")] = None
    answer_skills: Annotated[list[str] | None, Field(alias="answerSkills")] = None


class MergeCRMSourceConfig(SourceConfig):
    tenant: str | None = None
    description: str | None = None


class MergeFileStorageSourceConfig(SourceConfig):
    folders: list[MgFolder] | None = None
    drives: list[MgDrive] | None = None
    description: str | None = None


class MergeTicketingSourceConfig(SourceConfig):
    description: str | None = None


class ObjectFacet(GuruModel):
    id: str | None = None
    type: Type10 | None = None
    field: ObjectField | None = None
    tag_config: Annotated[ObjectTagConfig | None, Field(alias="tagConfig")] = None
    name: str | None = None
    allow_multiple_values: Annotated[bool | None, Field(alias="allowMultipleValues")] = None
    target_type: Annotated[TargetType | None, Field(alias="targetType")] = None
    template: str | None = None
    override_data_type: Annotated[OverrideDataType | None, Field(alias="overrideDataType")] = None
    hierarchical: bool | None = None
    data_type: Annotated[DataType | None, Field(alias="dataType")] = None


class Person(GuruModel):
    display_name: Annotated[str | None, Field(alias="displayName")] = None
    manager: Person | None = None
    deleted: bool | None = None
    direct_reports: Annotated[list[Person] | None, Field(alias="directReports")] = None
    pronouns: str | None = None
    job_title: Annotated[str | None, Field(alias="jobTitle")] = None
    work_team_name: Annotated[str | None, Field(alias="workTeamName")] = None
    work_team_id: Annotated[str | None, Field(alias="workTeamId")] = None
    work_location_name: Annotated[str | None, Field(alias="workLocationName")] = None
    work_location_id: Annotated[str | None, Field(alias="workLocationId")] = None
    working_hours: Annotated[str | None, Field(alias="workingHours")] = None
    working_timezone: Annotated[str | None, Field(alias="workingTimezone")] = None
    phone_number: Annotated[str | None, Field(alias="phoneNumber")] = None
    linked_in_profile: Annotated[str | None, Field(alias="linkedInProfile")] = None
    slack_profile_details: Annotated[
        list[InternalProfileSlackDetail] | None, Field(alias="slackProfileDetails")
    ] = None
    ms_teams_profile_url: Annotated[str | None, Field(alias="msTeamsProfileUrl")] = None
    synced_fields: Annotated[list[str] | None, Field(alias="syncedFields")] = None
    total_num_direct_reports: Annotated[int | None, Field(alias="totalNumDirectReports")] = None
    synced: bool | None = None
    start_date: Annotated[str | None, Field(alias="startDate")] = None
    user_id: Annotated[str | None, Field(alias="userId")] = None
    id: Annotated[str | None, Field(description="The identifier of this User")] = None
    user_profile: Annotated[
        UserProfile | None,
        Field(alias="userProfile", description="Additional information about a user"),
    ] = None
    last_name: Annotated[
        str | None, Field(alias="lastName", description="The user's last name")
    ] = None
    first_name: Annotated[
        str | None, Field(alias="firstName", description="The user's first name")
    ] = None
    profile_pic_url: Annotated[
        str | None,
        Field(alias="profilePicUrl", description="The profile picture url for the user"),
    ] = None
    joined_date: Annotated[AwareDatetime | None, Field(alias="joinedDate")] = None
    extended_info: Annotated[UserExtendedInfo | None, Field(alias="extendedInfo")] = None
    user_type: Annotated[UserType | None, Field(alias="userType")] = None
    status: Annotated[
        Status4 | None,
        Field(
            description="The status of a User can be ACTIVE or PENDING. The User must verify their email address to be considered ACTIVE."
        ),
    ] = None
    email: Annotated[str, Field(description="The user's email address")]
    custom: dict[str, dict[str, Any]] | None = None


class PromptTestConfig(GuruModel):
    question: str | None = None
    prompt_test_params: Annotated[PromptTestParams | None, Field(alias="promptTestParams")] = None


class QualityAgentRunDetailUpdate(GuruModel):
    confidence_score: Annotated[float | None, Field(alias="confidenceScore")] = None
    action_notes: Annotated[str | None, Field(alias="actionNotes")] = None
    action: Action1 | None = None
    usages: list[TokenUsage] | None = None


class QualityConfigEntry(GuruModel):
    verification_rules: Annotated[list[QualityRule] | None, Field(alias="verificationRules")] = None
    enabled: bool | None = None


class QuerySpec(GuruModel):
    query: Expression | None = None
    collection_ids: Annotated[list[str] | None, Field(alias="collectionIds")] = None
    sorts: list[Sort] | None = None
    query_type: Annotated[QueryType | None, Field(alias="queryType")] = None
    search_terms: Annotated[str | None, Field(alias="searchTerms")] = None
    max_results: Annotated[int | None, Field(alias="maxResults")] = None
    phrase: str | None = None
    show_archived: Annotated[bool | None, Field(alias="showArchived")] = None
    collection_uids: Annotated[list[int] | None, Field(alias="collectionUids")] = None
    source_ids: Annotated[list[str] | None, Field(alias="sourceIds")] = None
    start_index: Annotated[int | None, Field(alias="startIndex")] = None


class RecommendedForYouWidget(Widget):
    pass


class SampleSourceConfig(SourceConfig):
    name: str | None = None
    description: str | None = None
    icon_url: Annotated[str | None, Field(alias="iconUrl")] = None
    icon_data: Annotated[str | None, Field(alias="iconData")] = None
    icon_media_type: Annotated[str | None, Field(alias="iconMediaType")] = None


class SearchQuerySpec(GuruModel):
    include_facets: Annotated[bool | None, Field(alias="includeFacets")] = None
    include_snippets: Annotated[bool | None, Field(alias="includeSnippets")] = None
    include_content: Annotated[bool | None, Field(alias="includeContent")] = None
    source_types: Annotated[list[str] | None, Field(alias="sourceTypes")] = None
    agent_id: Annotated[str | None, Field(alias="agentId")] = None
    query: Expression | None = None
    collection_ids: Annotated[list[str] | None, Field(alias="collectionIds")] = None
    sorts: list[Sort] | None = None
    query_type: Annotated[QueryType | None, Field(alias="queryType")] = None
    search_terms: Annotated[str | None, Field(alias="searchTerms")] = None
    max_results: Annotated[int | None, Field(alias="maxResults")] = None
    phrase: str | None = None
    show_archived: Annotated[bool | None, Field(alias="showArchived")] = None
    collection_uids: Annotated[list[int] | None, Field(alias="collectionUids")] = None
    source_ids: Annotated[list[str] | None, Field(alias="sourceIds")] = None
    start_index: Annotated[int | None, Field(alias="startIndex")] = None


class SlackSourceConfig(SourceConfig):
    slack_team_name: Annotated[str | None, Field(alias="slackTeamName")] = None
    channel_id: Annotated[str | None, Field(alias="channelId")] = None
    channel_name: Annotated[str | None, Field(alias="channelName")] = None
    exclude_bot_messages: Annotated[bool | None, Field(alias="excludeBotMessages")] = None
    is_private_channel: Annotated[bool | None, Field(alias="isPrivateChannel")] = None
    use_top_message_as_title: Annotated[bool | None, Field(alias="useTopMessageAsTitle")] = None
    description: str | None = None


class SourceDefinition(GuruModel):
    name: str | None = None
    id: str | None = None
    type: str | None = None
    icon_url: Annotated[str | None, Field(alias="iconUrl")] = None
    category: str | None = None
    config_type: Annotated[ConfigType | None, Field(alias="configType")] = None
    availability: Availability | None = None
    request_access: Annotated[bool | None, Field(alias="requestAccess")] = None
    manual_sync_allowed: Annotated[bool | None, Field(alias="manualSyncAllowed")] = None
    supports_dynamic_display_properties: Annotated[
        bool | None, Field(alias="supportsDynamicDisplayProperties")
    ] = None
    description: str | None = None
    config: SourceDefinitionConfig | None = None


class SourceFacet(GuruModel):
    id: str | None = None
    name: str | None = None
    count: int | None = None
    gld_object_types: Annotated[list[GldObjectTypeFacet] | None, Field(alias="gldObjectTypes")] = (
        None
    )


class User(GuruModel):
    id: Annotated[str | None, Field(description="The identifier of this User")] = None
    user_profile: Annotated[
        UserProfile | None,
        Field(alias="userProfile", description="Additional information about a user"),
    ] = None
    last_name: Annotated[
        str | None, Field(alias="lastName", description="The user's last name")
    ] = None
    first_name: Annotated[
        str | None, Field(alias="firstName", description="The user's first name")
    ] = None
    profile_pic_url: Annotated[
        str | None,
        Field(alias="profilePicUrl", description="The profile picture url for the user"),
    ] = None
    joined_date: Annotated[AwareDatetime | None, Field(alias="joinedDate")] = None
    extended_info: Annotated[UserExtendedInfo | None, Field(alias="extendedInfo")] = None
    user_type: Annotated[UserType | None, Field(alias="userType")] = None
    status: Annotated[
        Status7 | None,
        Field(
            description="The status of a User can be ACTIVE or PENDING. The User must verify their email address to be considered ACTIVE."
        ),
    ] = None
    email: Annotated[str, Field(description="The user's email address")]


class UserCollaborator(CardCollaborator):
    user: Annotated[User, Field(description="The collaborator")]


class UserFollower(GuruModel):
    user: User | None = None
    date_followed: Annotated[AwareDatetime | None, Field(alias="dateFollowed")] = None


class UserGroupMember(GuruModel):
    id: Annotated[str | None, Field(description="ID of the group member")] = None
    date_created: Annotated[
        AwareDatetime | None,
        Field(
            alias="dateCreated",
            description="Date the group member was added to the group. Dates are in ISO-8601 format. Example date (January 2nd 2014 12pm UTC): 2014-01-02T12:00:00.000+0000",
        ),
    ] = None
    managed_by_scim: Annotated[bool | None, Field(alias="managedByScim")] = None
    user: Annotated[User, Field(description="The group member")]


class UserVerifier(CardVerifier):
    user: Annotated[User, Field(description="The verifier")]


class CardCommentReply(GuruModel):
    id: Annotated[str | None, Field(description="ID of the comment reply")] = None
    content: Annotated[str, Field(description="Comment content (max length: 2500 characters)")]
    owner: Annotated[User | None, Field(description="The owner of the comment")] = None
    last_modified: Annotated[
        AwareDatetime | None,
        Field(
            alias="lastModified",
            description="Date the comment was last modified. Dates are in ISO-8601 format. Example date (January 2nd 2014 12pm UTC): 2014-01-02T12:00:00.000+0000",
        ),
    ] = None
    deleted: Annotated[
        bool | None, Field(description="Indicates if the comment has been deleted")
    ] = None
    date_created: Annotated[
        AwareDatetime | None,
        Field(
            alias="dateCreated",
            description="Date the comment was created. Dates are in ISO-8601 format. Example date (January 2nd 2014 12pm UTC): 2014-01-02T12:00:00.000+0000",
        ),
    ] = None
    reactions: list[ReactionDetail] | None = None


class CardVerifiers(GuruModel):
    verifiers: list[CardVerifier] | None = None
    verification_state: Annotated[VerificationState | None, Field(alias="verificationState")] = None
    verification_reason: Annotated[VerificationReason | None, Field(alias="verificationReason")] = (
        None
    )
    verification_initiator: Annotated[User | None, Field(alias="verificationInitiator")] = None


class Document(GuruModel):
    id: str | None = None
    content: str | None = None
    last_modified: Annotated[AwareDatetime | None, Field(alias="lastModified")] = None
    version: int | None = None
    deleted: bool | None = None
    date_created: Annotated[AwareDatetime | None, Field(alias="dateCreated")] = None
    last_verified: Annotated[AwareDatetime | None, Field(alias="lastVerified")] = None
    last_verified_by: Annotated[User | None, Field(alias="lastVerifiedBy")] = None
    verification_state: Annotated[VerificationState | None, Field(alias="verificationState")] = None
    last_verification_modified_by_type: Annotated[
        LastVerificationModifiedByType | None,
        Field(alias="lastVerificationModifiedByType"),
    ] = None
    last_verification_notes: Annotated[str | None, Field(alias="lastVerificationNotes")] = None
    last_verification_action_date: Annotated[
        AwareDatetime | None, Field(alias="lastVerificationActionDate")
    ] = None
    last_verification_confidence_score: Annotated[
        float | None, Field(alias="lastVerificationConfidenceScore")
    ] = None
    inaccessible_to_asker: Annotated[bool | None, Field(alias="inaccessibleToAsker")] = None
    inaccessible: bool | None = None
    latest_version: Annotated[int | None, Field(alias="latestVersion")] = None
    included_in_prompt: Annotated[bool | None, Field(alias="includedInPrompt")] = None
    url: str | None = None
    title: str | None = None
    document_type: Annotated[DocumentType, Field(alias="documentType")]


class McpDocument(Document):
    tool_name: Annotated[str | None, Field(alias="toolName")] = None
    tool_call_id: Annotated[str | None, Field(alias="toolCallId")] = None
    mcp_display_name: Annotated[str | None, Field(alias="mcpDisplayName")] = None
    mcp_icon_url: Annotated[str | None, Field(alias="mcpIconUrl")] = None


class QualityAgentRunDetail(GuruModel):
    mode: Mode | None = None
    submitted_date: Annotated[AwareDatetime | None, Field(alias="submittedDate")] = None
    completion_date: Annotated[AwareDatetime | None, Field(alias="completionDate")] = None
    confidence_score: Annotated[float | None, Field(alias="confidenceScore")] = None
    action_notes: Annotated[str | None, Field(alias="actionNotes")] = None
    action: Action1 | None = None
    document: Document | None = None


class QualityConfig(GuruModel):
    config: dict[str, QualityConfigEntry] | None = None


class ScheduleArchivalResponse(GuruModel):
    card_id: Annotated[
        str | None,
        Field(
            alias="cardId",
            description="The ID of the card scheduled for archival",
            examples=["IDs are formatted like this: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"],
        ),
    ] = None
    scheduled_archive_date: Annotated[
        AwareDatetime | None,
        Field(
            alias="scheduledArchiveDate",
            description="The date when the card will be archived",
            examples=[
                "Dates are in ISO-8601 format. Example date (January 2nd 2014 12pm UTC): 2014-01-02T12:00:00.000+0000"
            ],
        ),
    ] = None
    scheduled_by: Annotated[
        User | None,
        Field(alias="scheduledBy", description="The user who scheduled the archival"),
    ] = None
    date_scheduled: Annotated[
        AwareDatetime | None,
        Field(
            alias="dateScheduled",
            description="The date when the archival was scheduled",
            examples=[
                "Dates are in ISO-8601 format. Example date (January 2nd 2014 12pm UTC): 2014-01-02T12:00:00.000+0000"
            ],
        ),
    ] = None


class SearchFacets(GuruModel):
    collections: list[CollectionFacet] | None = None
    tags: list[TagFacet] | None = None
    authors: list[AuthorsFacet] | None = None
    sources: list[SourceFacet] | None = None
    source_types: Annotated[list[SourceTypeFacet] | None, Field(alias="sourceTypes")] = None


class WebDocument(Document):
    web_search_icon_url: Annotated[str | None, Field(alias="webSearchIconUrl")] = None


class AnswerExplanation(GuruModel):
    search_terms: Annotated[list[str] | None, Field(alias="searchTerms")] = None
    explanation: str | None = None
    relevant_sources: Annotated[list[Document] | None, Field(alias="relevantSources")] = None
    search_criteria: Annotated[SearchQuerySpec | None, Field(alias="searchCriteria")] = None


class CardAttachment(GuruModel):
    id: Annotated[
        str | None,
        Field(
            description="The ID of the CardAttachment",
            examples=["IDs are formatted like this: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"],
        ),
    ] = None
    size: Annotated[
        int | None,
        Field(description="The attached file's size in bytes", examples=[1000]),
    ] = None
    extension: Annotated[
        str | None, Field(description="The attached file's extension", examples=["csv"])
    ] = None
    document: Document | None = None
    link: Annotated[
        str | None,
        Field(description="Link to where the uploaded file is hosted in Guru's servers"),
    ] = None
    thumbnail_link: Annotated[
        str | None,
        Field(
            alias="thumbnailLink",
            description="Link to where the thumbnail for the uploaded file is hosted in Guru's servers",
        ),
    ] = None
    previewable: bool | None = None
    mimetype: str | None = None
    filename: Annotated[
        str | None,
        Field(description="The file name and extension", examples=["file-name.png"]),
    ] = None


class CardAttachmentDocument(Document):
    size: int | None = None
    extension: str | None = None
    previewable: bool | None = None
    mimetype: str | None = None


class CardComment(GuruModel):
    id: Annotated[str | None, Field(description="ID of the comment")] = None
    total_replies: Annotated[
        int | None,
        Field(alias="totalReplies", description="Number of total replies on the comment"),
    ] = None
    replies: Annotated[
        list[CardCommentReply] | None,
        Field(
            description="The most recent replies to the comment. If the totalReplies property is greater than the number of replies in this list, additional replies can be found through the Get Replies endpoint."
        ),
    ] = None
    extra_details_model: Annotated[
        ExtraDetailsModel | None,
        Field(
            alias="extraDetailsModel",
            description="Extra details such as whether the comment corresponds to an announcement",
        ),
    ] = None
    status: Annotated[Status3 | None, Field(description="Status of the comment")] = None
    content: Annotated[str, Field(description="Comment content (max length: 2500 characters)")]
    owner: Annotated[User | None, Field(description="The owner of the comment")] = None
    last_modified: Annotated[
        AwareDatetime | None,
        Field(
            alias="lastModified",
            description="Date the comment was last modified. Dates are in ISO-8601 format. Example date (January 2nd 2014 12pm UTC): 2014-01-02T12:00:00.000+0000",
        ),
    ] = None
    deleted: Annotated[
        bool | None, Field(description="Indicates if the comment has been deleted")
    ] = None
    date_created: Annotated[
        AwareDatetime | None,
        Field(
            alias="dateCreated",
            description="Date the comment was created. Dates are in ISO-8601 format. Example date (January 2nd 2014 12pm UTC): 2014-01-02T12:00:00.000+0000",
        ),
    ] = None
    reactions: list[ReactionDetail] | None = None


class ChatMessage(GuruModel):
    id: str | None = None
    content: str | None = None
    role: Role | None = None
    date_created: Annotated[AwareDatetime | None, Field(alias="dateCreated")] = None
    chat_mode: Annotated[ChatMode | None, Field(alias="chatMode")] = None
    type: Type3 | None = None
    turn_id: Annotated[str | None, Field(alias="turnId")] = None
    metadata: ChatMessageMetadata | None = None
    approval_action: Annotated[SimpleApprovalAction | None, Field(alias="approvalAction")] = None
    mcp_tool_approvals: Annotated[
        list[McpToolPermissionApproval] | None, Field(alias="mcpToolApprovals")
    ] = None
    answer_mode: Annotated[AnswerMode | None, Field(alias="answerMode")] = None
    documents: list[Document] | None = None


class DocumentSearchResponse(GuruModel):
    total: int | None = None
    facets: SearchFacets | None = None
    documents: list[Document] | None = None


class NLQSearchResponse(GuruModel):
    query_spec: Annotated[SearchQuerySpec | None, Field(alias="querySpec")] = None
    total: int | None = None
    facets: SearchFacets | None = None
    documents: list[Document] | None = None


class AnnouncementInsightSummary(GuruModel):
    announcement: KnowledgeAlert | None = None
    read_users: Annotated[list[AnnouncementUser] | None, Field(alias="readUsers")] = None
    current_user_announcement_user: Annotated[
        bool | None, Field(alias="currentUserAnnouncementUser")
    ] = None
    unopened_count: Annotated[int | None, Field(alias="unopenedCount")] = None
    opened_count: Annotated[int | None, Field(alias="openedCount")] = None
    read_count: Annotated[int | None, Field(alias="readCount")] = None
    unread_count: Annotated[int | None, Field(alias="unreadCount")] = None
    current_user_read_date: Annotated[AwareDatetime | None, Field(alias="currentUserReadDate")] = (
        None
    )


class Answer(GuruModel):
    answer: str | None = None
    answer_id: Annotated[str | None, Field(alias="answerId")] = None
    sources: list[Document] | None = None
    latest_feedback: Annotated[LatestFeedback | None, Field(alias="latestFeedback")] = None
    asker: User | None = None
    answer_date: Annotated[AwareDatetime | None, Field(alias="answerDate")] = None
    status: Status1 | None = None
    question: str | None = None
    linked_question: Annotated[Card | None, Field(alias="linkedQuestion")] = None
    linked_question_assignee: Annotated[
        CardVerifier | None, Field(alias="linkedQuestionAssignee")
    ] = None
    answered: bool | None = None
    preview_answer_id: Annotated[str | None, Field(alias="previewAnswerId")] = None
    answerer: User | None = None
    search_assistant: Annotated[KnowledgeAgent | None, Field(alias="searchAssistant")] = None
    can_edit: Annotated[bool | None, Field(alias="canEdit")] = None
    answer_explanation: Annotated[AnswerExplanation | None, Field(alias="answerExplanation")] = None
    last_modified: Annotated[AwareDatetime | None, Field(alias="lastModified")] = None
    deleted: bool | None = None
    chat_thread_id: Annotated[str | None, Field(alias="chatThreadId")] = None
    suggested_questions: Annotated[SuggestedQuestions | None, Field(alias="suggestedQuestions")] = (
        None
    )
    restrictions: list[Restriction] | None = None
    external_url: Annotated[str | None, Field(alias="externalUrl")] = None
    thread_type: Annotated[ThreadType | None, Field(alias="threadType")] = None


class Application(GuruModel):
    name: str | None = None
    id: str | None = None
    source: Source | None = None
    relationships: list[Relationship] | None = None
    object_types: Annotated[list[ObjectType] | None, Field(alias="objectTypes")] = None


class AutomationPlan(GuruModel):
    name: Annotated[str | None, Field(description="The name of the automation plan")] = None
    id: Annotated[
        str | None, Field(description="The unique identifier for the automation plan")
    ] = None
    content: Annotated[str | None, Field(description="The automation plan content/prompt")] = None
    created_by: Annotated[
        User | None,
        Field(alias="createdBy", description="The user who created the automation plan"),
    ] = None
    modified_date: Annotated[
        AwareDatetime | None,
        Field(
            alias="modifiedDate",
            description="The date the automation plan was last modified",
        ),
    ] = None
    created_date: Annotated[
        AwareDatetime | None,
        Field(alias="createdDate", description="The date the automation plan was created"),
    ] = None
    next_run_date: Annotated[
        AwareDatetime | None,
        Field(
            alias="nextRunDate",
            description="The date the automation plan is scheduled to run next",
        ),
    ] = None
    cron_schedule: Annotated[
        str | None,
        Field(
            alias="cronSchedule",
            description="The cron schedule for when to run the automation plan",
        ),
    ] = None
    knowledge_agent: Annotated[
        KnowledgeAgent | None,
        Field(
            alias="knowledgeAgent",
            description="The knowledge agent that will execute the automation plan",
        ),
    ] = None
    last_run_date: Annotated[
        AwareDatetime | None,
        Field(alias="lastRunDate", description="The date the automation plan was last run"),
    ] = None
    last_run: Annotated[
        ChatThread | None,
        Field(
            alias="lastRun",
            description="The last chat thread created by this automation plan",
        ),
    ] = None
    status: Annotated[
        Status2 | None, Field(description="The current status of the automation plan")
    ] = None


class BasePage(GuruModel):
    permissions: list[Permission] | None = None
    id: Annotated[
        str | None,
        Field(
            description="The ID of the object",
            examples=["IDs are formatted like this: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"],
        ),
    ] = None
    last_modified: Annotated[
        AwareDatetime | None,
        Field(
            alias="lastModified",
            description="The date that the object was last modified",
            examples=[
                "Dates are in ISO-8601 format. Example date (January 2nd 2014 12pm UTC): 2014-01-02T12:00:00.000+0000"
            ],
        ),
    ] = None
    team: Annotated[Team | None, Field(description="The team that the object is on")] = None
    date_created: Annotated[
        AwareDatetime | None,
        Field(
            alias="dateCreated",
            description="The date that the object was created",
            examples=[
                "Dates are in ISO-8601 format. Example date (January 2nd 2014 12pm UTC): 2014-01-02T12:00:00.000+0000"
            ],
        ),
    ] = None
    last_modified_by: Annotated[
        User | None,
        Field(alias="lastModifiedBy", description="The last user who modified the object"),
    ] = None
    json_content: Annotated[
        str | None,
        Field(alias="jsonContent", description="The json content of the page"),
    ] = None
    draft: Annotated[bool | None, Field(description="Indicates if this is a draft")] = None
    hero_image: Annotated[
        str | None, Field(alias="heroImage", description="The hero image link")
    ] = None
    badge_emoji: Annotated[
        str | None,
        Field(
            alias="badgeEmoji",
            description="An emoji value for the badge of the page",
            examples=[":star:"],
        ),
    ] = None
    parent_page_id: Annotated[
        str | None, Field(alias="parentPageId", description="The ID of the parent page")
    ] = None
    sub_pages: Annotated[
        list[BasePage] | None,
        Field(alias="subPages", description="An ordered list of sub-pages"),
    ] = None
    only_navigable: Annotated[
        bool | None,
        Field(
            alias="onlyNavigable",
            description="Indicates if the page is only visible for navigation purposes",
        ),
    ] = None
    knowledge_agent_id: Annotated[
        str | None,
        Field(
            alias="knowledgeAgentId",
            description="The ID of the default Knowledge Agent for this page",
        ),
    ] = None
    editable: Annotated[
        bool | None,
        Field(description="Indicates if this is editable by the current user"),
    ] = None
    title: Annotated[str | None, Field(description="The title of the page")] = None


class Card(GuruModel):
    permissions: list[Permission] | None = None
    id: Annotated[
        str | None,
        Field(
            description="ID of the Card",
            examples=["IDs are formatted like this: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"],
        ),
    ] = None
    content: Annotated[
        str,
        Field(
            description="The Card's HTML or Markdown content",
            examples=["Here's some **awesome content**"],
        ),
    ]
    owner: Annotated[User | None, Field(description="The User object of the owner of the card")] = (
        None
    )
    last_modified: Annotated[
        AwareDatetime | None,
        Field(
            alias="lastModified",
            description="Date the Card was last modified",
            examples=[
                "Dates are in ISO-8601 format. Example date (January 2nd 2014 12pm UTC): 2014-01-02T12:00:00.000+0000"
            ],
        ),
    ] = None
    version: Annotated[
        int | None,
        Field(
            description="Current version of the Card. As the card gets updated and revised, the version number will increase.",
            examples=[1],
        ),
    ] = None
    collection: Annotated[
        CollectionModel | None, Field(description="The Collection the Card belongs to")
    ] = None
    date_created: Annotated[
        AwareDatetime | None,
        Field(
            alias="dateCreated",
            description="Date the Card was created",
            examples=[
                "Dates are in ISO-8601 format. Example date (January 2nd 2014 12pm UTC): 2014-01-02T12:00:00.000+0000"
            ],
        ),
    ] = None
    favorited_date: Annotated[
        AwareDatetime | None,
        Field(
            alias="favoritedDate",
            description="Date when this card has been favorited by the current user",
        ),
    ] = None
    slug: Annotated[
        str | None,
        Field(
            description="The slug is the URL address to the card",
            examples=["https://app.getguru.com/cards/:slug_goes_here"],
        ),
    ] = None
    last_verified: Annotated[
        AwareDatetime | None,
        Field(
            alias="lastVerified",
            description="Date the Card was last verified",
            examples=[
                "Dates are in ISO-8601 format. Example date (January 2nd 2014 12pm UTC): 2014-01-02T12:00:00.000+0000"
            ],
        ),
    ] = None
    last_verified_by: Annotated[
        User | None,
        Field(alias="lastVerifiedBy", description="The User to last verify the Card"),
    ] = None
    last_modified_by: Annotated[
        User | None,
        Field(alias="lastModifiedBy", description="The User to last modify the Card"),
    ] = None
    preferred_phrase: Annotated[
        str,
        Field(
            alias="preferredPhrase",
            description="The title of the Card",
            examples=["My New Card"],
        ),
    ]
    boards: Annotated[
        list[dict[str, Any]] | None,
        Field(description="Returns Board objects that this card appears on"),
    ] = None
    share_status: Annotated[
        ShareStatus | None,
        Field(
            alias="shareStatus",
            description="The share status of the Card.  TEAM for team shared cards and PRIVATE for privately shared cards",
            examples=["TEAM"],
        ),
    ] = None
    suppress_verification: Annotated[
        bool | None,
        Field(
            alias="suppressVerification",
            description="Flag for enabling card verification on save",
        ),
    ] = None
    verification_interval: Annotated[
        int | None,
        Field(
            alias="verificationInterval",
            description="Time interval (in days), indicating the frequency that this card needs re-verification. Passing in null will default to 30 days.",
        ),
    ] = None
    verifiers: Annotated[
        list[CardVerifier] | None,
        Field(description="Users/Groups that are responsible for verifying this card"),
    ] = None
    verification_type: Annotated[
        VerificationType | None,
        Field(
            alias="verificationType",
            description="Whether the card's verification date is ABSOLUTE or RELATIVE",
        ),
    ] = None
    collaborators: Annotated[
        list[CardCollaborator] | None,
        Field(
            description="Users/Groups that this card is explicitly shared to. Collaborators of a card are the only ones who have access if the Card's shareStatus is PRIVATE."
        ),
    ] = None
    verification_state: Annotated[
        VerificationState | None,
        Field(
            alias="verificationState",
            description="Whether the card is TRUSTED, STALE, or NEEDS_VERIFICATION",
        ),
    ] = None
    verification_reason: Annotated[
        VerificationReason | None,
        Field(
            alias="verificationReason",
            description="Reason this card needs verification.  UPDATE if this card was updated by a user that is not the verifier. NEW_VERIFIER if this card was assigned to a new verifier but has not yet been verified.  This value will only be present if the verification state is NEEDS_VERIFICATION",
        ),
    ] = None
    public_link_allowed: Annotated[bool | None, Field(alias="publicLinkAllowed")] = None
    archived: Annotated[
        bool | None, Field(description="Indicates if the Card has been archived")
    ] = None
    next_verification_date: Annotated[
        AwareDatetime | None,
        Field(
            alias="nextVerificationDate",
            description="Next date that this Card needs verification dependent on verification interval",
            examples=[
                "Dates are in ISO-8601 format. Example date (January 2nd 2014 12pm UTC): 2014-01-02T12:00:00.000+0000"
            ],
        ),
    ] = None
    original_owner: Annotated[
        User | None,
        Field(
            alias="originalOwner",
            description="The User object of the original owner of the card",
        ),
    ] = None
    last_viewed: Annotated[
        AwareDatetime | None,
        Field(
            alias="lastViewed",
            description="Last time the card was viewed",
            examples=[
                "Dates are in ISO-8601 format. Example date (January 2nd 2014 12pm UTC): 2014-01-02T12:00:00.000+0000"
            ],
        ),
    ] = None
    favorited: Annotated[
        bool | None,
        Field(description="Whether this card has been favorited by the current user"),
    ] = None
    attachments: Annotated[
        list[CardAttachment] | None, Field(description="Attachments to the card")
    ] = None
    verification_reasons: Annotated[
        list[VerificationReason] | None, Field(alias="verificationReasons")
    ] = None
    verification_initiator: Annotated[
        User | None,
        Field(
            alias="verificationInitiator",
            description="User corresponding to the action that caused the card to need verification.",
        ),
    ] = None
    comment_count: Annotated[
        int | None,
        Field(alias="commentCount", description="Number of comments on the card"),
    ] = None
    card_info: Annotated[CardInfo | None, Field(alias="cardInfo")] = None
    sync_info: Annotated[
        CardSyncInfo | None,
        Field(
            alias="syncInfo",
            description="Returns an object about Sync information, if this card is from a synced Collection. Information includes: externalUrl, lastSyncDate, lastUpdateDate, and syncType.",
        ),
    ] = None
    verification_initiation_date: Annotated[
        AwareDatetime | None,
        Field(
            alias="verificationInitiationDate",
            description="Date corresponding to the action that unverified the card",
        ),
    ] = None
    card_template_id: Annotated[
        str | None,
        Field(
            alias="cardTemplateId",
            description="ID of the template from which this card was created if applicable",
        ),
    ] = None
    folder_count: Annotated[
        int | None,
        Field(alias="folderCount", description="The number of folders this card is in"),
    ] = None
    answer_id: Annotated[str | None, Field(alias="answerId")] = None
    comments_enabled: Annotated[
        bool | None,
        Field(
            alias="commentsEnabled",
            description="A flag to indicate if comments are allowed on this Card",
        ),
    ] = None
    pending_auto_archive: Annotated[
        bool | None,
        Field(
            alias="pendingAutoArchive",
            description="A flag to indicate if this unverified card is currently in an auto archive queue",
        ),
    ] = None
    settings_update: Annotated[
        bool | None,
        Field(
            alias="settingsUpdate",
            description="A flag to indicate if the changes are only updating the settings of the card",
        ),
    ] = None
    last_verification_modified_by_type: Annotated[
        LastVerificationModifiedByType | None,
        Field(alias="lastVerificationModifiedByType"),
    ] = None
    last_verification_notes: Annotated[str | None, Field(alias="lastVerificationNotes")] = None
    last_verification_action_date: Annotated[
        AwareDatetime | None, Field(alias="lastVerificationActionDate")
    ] = None
    last_verification_confidence_score: Annotated[
        float | None, Field(alias="lastVerificationConfidenceScore")
    ] = None
    quality_check_allowed: Annotated[bool | None, Field(alias="qualityCheckAllowed")] = None
    card_type: Annotated[str | None, Field(alias="cardType")] = None
    tags: Annotated[
        list[Tag] | None,
        Field(description="Returns Tag objects associated with this card"),
    ] = None


class CardDocument(Document):
    user_allowed_to_verify: Annotated[bool | None, Field(alias="userAllowedToVerify")] = None
    id: Annotated[
        str | None,
        Field(
            description="ID of the Card",
            examples=["IDs are formatted like this: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"],
        ),
    ] = None
    content: Annotated[
        str,
        Field(
            description="The Card's HTML or Markdown content",
            examples=["Here's some **awesome content**"],
        ),
    ]
    last_modified: Annotated[
        AwareDatetime | None,
        Field(
            alias="lastModified",
            description="Date the Card was last modified",
            examples=[
                "Dates are in ISO-8601 format. Example date (January 2nd 2014 12pm UTC): 2014-01-02T12:00:00.000+0000"
            ],
        ),
    ] = None
    version: Annotated[
        int | None,
        Field(
            description="Current version of the Card. As the card gets updated and revised, the version number will increase.",
            examples=[1],
        ),
    ] = None
    date_created: Annotated[
        AwareDatetime | None,
        Field(
            alias="dateCreated",
            description="Date the Card was created",
            examples=[
                "Dates are in ISO-8601 format. Example date (January 2nd 2014 12pm UTC): 2014-01-02T12:00:00.000+0000"
            ],
        ),
    ] = None
    last_verified: Annotated[
        AwareDatetime | None,
        Field(
            alias="lastVerified",
            description="Date the Card was last verified",
            examples=[
                "Dates are in ISO-8601 format. Example date (January 2nd 2014 12pm UTC): 2014-01-02T12:00:00.000+0000"
            ],
        ),
    ] = None
    last_verified_by: Annotated[
        User | None,
        Field(alias="lastVerifiedBy", description="The User to last verify the Card"),
    ] = None
    verification_state: Annotated[
        VerificationState | None,
        Field(
            alias="verificationState",
            description="Whether the card is TRUSTED, STALE, or NEEDS_VERIFICATION",
        ),
    ] = None
    permissions: list[Permission] | None = None
    owner: Annotated[User | None, Field(description="The User object of the owner of the card")] = (
        None
    )
    collection: Annotated[
        CollectionModel | None, Field(description="The Collection the Card belongs to")
    ] = None
    favorited_date: Annotated[
        AwareDatetime | None,
        Field(
            alias="favoritedDate",
            description="Date when this card has been favorited by the current user",
        ),
    ] = None
    slug: Annotated[
        str | None,
        Field(
            description="The slug is the URL address to the card",
            examples=["https://app.getguru.com/cards/:slug_goes_here"],
        ),
    ] = None
    last_modified_by: Annotated[
        User | None,
        Field(alias="lastModifiedBy", description="The User to last modify the Card"),
    ] = None
    boards: Annotated[
        list[dict[str, Any]] | None,
        Field(description="Returns Board objects that this card appears on"),
    ] = None
    share_status: Annotated[
        ShareStatus | None,
        Field(
            alias="shareStatus",
            description="The share status of the Card.  TEAM for team shared cards and PRIVATE for privately shared cards",
            examples=["TEAM"],
        ),
    ] = None
    suppress_verification: Annotated[
        bool | None,
        Field(
            alias="suppressVerification",
            description="Flag for enabling card verification on save",
        ),
    ] = None
    verification_interval: Annotated[
        int | None,
        Field(
            alias="verificationInterval",
            description="Time interval (in days), indicating the frequency that this card needs re-verification. Passing in null will default to 30 days.",
        ),
    ] = None
    verifiers: Annotated[
        list[CardVerifier] | None,
        Field(description="Users/Groups that are responsible for verifying this card"),
    ] = None
    verification_type: Annotated[
        VerificationType | None,
        Field(
            alias="verificationType",
            description="Whether the card's verification date is ABSOLUTE or RELATIVE",
        ),
    ] = None
    collaborators: Annotated[
        list[CardCollaborator] | None,
        Field(
            description="Users/Groups that this card is explicitly shared to. Collaborators of a card are the only ones who have access if the Card's shareStatus is PRIVATE."
        ),
    ] = None
    verification_reason: Annotated[
        VerificationReason | None,
        Field(
            alias="verificationReason",
            description="Reason this card needs verification.  UPDATE if this card was updated by a user that is not the verifier. NEW_VERIFIER if this card was assigned to a new verifier but has not yet been verified.  This value will only be present if the verification state is NEEDS_VERIFICATION",
        ),
    ] = None
    public_link_allowed: Annotated[bool | None, Field(alias="publicLinkAllowed")] = None
    archived: Annotated[
        bool | None, Field(description="Indicates if the Card has been archived")
    ] = None
    next_verification_date: Annotated[
        AwareDatetime | None,
        Field(
            alias="nextVerificationDate",
            description="Next date that this Card needs verification dependent on verification interval",
            examples=[
                "Dates are in ISO-8601 format. Example date (January 2nd 2014 12pm UTC): 2014-01-02T12:00:00.000+0000"
            ],
        ),
    ] = None
    original_owner: Annotated[
        User | None,
        Field(
            alias="originalOwner",
            description="The User object of the original owner of the card",
        ),
    ] = None
    last_viewed: Annotated[
        AwareDatetime | None,
        Field(
            alias="lastViewed",
            description="Last time the card was viewed",
            examples=[
                "Dates are in ISO-8601 format. Example date (January 2nd 2014 12pm UTC): 2014-01-02T12:00:00.000+0000"
            ],
        ),
    ] = None
    favorited: Annotated[
        bool | None,
        Field(description="Whether this card has been favorited by the current user"),
    ] = None
    attachments: Annotated[
        list[CardAttachment] | None, Field(description="Attachments to the card")
    ] = None
    verification_reasons: Annotated[
        list[VerificationReason] | None, Field(alias="verificationReasons")
    ] = None
    verification_initiator: Annotated[
        User | None,
        Field(
            alias="verificationInitiator",
            description="User corresponding to the action that caused the card to need verification.",
        ),
    ] = None
    comment_count: Annotated[
        int | None,
        Field(alias="commentCount", description="Number of comments on the card"),
    ] = None
    card_info: Annotated[CardInfo | None, Field(alias="cardInfo")] = None
    sync_info: Annotated[
        CardSyncInfo | None,
        Field(
            alias="syncInfo",
            description="Returns an object about Sync information, if this card is from a synced Collection. Information includes: externalUrl, lastSyncDate, lastUpdateDate, and syncType.",
        ),
    ] = None
    verification_initiation_date: Annotated[
        AwareDatetime | None,
        Field(
            alias="verificationInitiationDate",
            description="Date corresponding to the action that unverified the card",
        ),
    ] = None
    card_template_id: Annotated[
        str | None,
        Field(
            alias="cardTemplateId",
            description="ID of the template from which this card was created if applicable",
        ),
    ] = None
    folder_count: Annotated[
        int | None,
        Field(alias="folderCount", description="The number of folders this card is in"),
    ] = None
    answer_id: Annotated[str | None, Field(alias="answerId")] = None
    comments_enabled: Annotated[
        bool | None,
        Field(
            alias="commentsEnabled",
            description="A flag to indicate if comments are allowed on this Card",
        ),
    ] = None
    pending_auto_archive: Annotated[
        bool | None,
        Field(
            alias="pendingAutoArchive",
            description="A flag to indicate if this unverified card is currently in an auto archive queue",
        ),
    ] = None
    settings_update: Annotated[
        bool | None,
        Field(
            alias="settingsUpdate",
            description="A flag to indicate if the changes are only updating the settings of the card",
        ),
    ] = None
    quality_check_allowed: Annotated[bool | None, Field(alias="qualityCheckAllowed")] = None
    card_type: Annotated[str | None, Field(alias="cardType")] = None
    tags: Annotated[
        list[Tag] | None,
        Field(description="Returns Tag objects associated with this card"),
    ] = None


class CardTemplate(GuruModel):
    id: str | None = None
    content: str | None = None
    last_modified: Annotated[AwareDatetime | None, Field(alias="lastModified")] = None
    collection: CollectionModel | None = None
    date_created: Annotated[AwareDatetime | None, Field(alias="dateCreated")] = None
    created_by: Annotated[User | None, Field(alias="createdBy")] = None
    last_modified_by: Annotated[User | None, Field(alias="lastModifiedBy")] = None
    boards: list[Folder] | None = None
    share_status: Annotated[ShareStatus | None, Field(alias="shareStatus")] = None
    verification_interval: Annotated[int | None, Field(alias="verificationInterval")] = None
    json_content: Annotated[str | None, Field(alias="jsonContent")] = None
    card_title: Annotated[str | None, Field(alias="cardTitle")] = None
    content_schema_version: Annotated[str | None, Field(alias="contentSchemaVersion")] = None
    template_title: Annotated[str | None, Field(alias="templateTitle")] = None
    card_verifier: Annotated[CardVerifier | None, Field(alias="cardVerifier")] = None
    description: str | None = None
    tags: list[Tag] | None = None


class ChatThread(GuruModel):
    id: str | None = None
    title: str | None = None
    date_created: Annotated[AwareDatetime | None, Field(alias="dateCreated")] = None
    knowledge_agent: Annotated[KnowledgeAgent | None, Field(alias="knowledgeAgent")] = None
    restrictions: list[Restriction] | None = None
    creator: User | None = None


class CollectionModel(GuruModel):
    name: Annotated[str | None, Field(description="Collection Name")] = None
    read_only: Annotated[bool | None, Field(alias="readOnly")] = None
    permissions: list[Permission] | None = None
    id: Annotated[
        str | None,
        Field(
            description="ID of the collection",
            examples=["IDs are formatted like this: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"],
        ),
    ] = None
    color: Annotated[
        str | None,
        Field(
            description="A hex value for the color of the Collection",
            examples=["#f44336"],
        ),
    ] = None
    deleted: Annotated[
        bool | None,
        Field(description="Flag for whether this Collection has been deleted"),
    ] = None
    team: Team | None = None
    default_verifier: Annotated[str | None, Field(alias="defaultVerifier")] = None
    sync_type: Annotated[
        SyncType | None,
        Field(
            alias="syncType",
            description="If this Collection has been synced, this will return the type. Types include: Zendesk, Confluence, Google Drive, and Manual.",
        ),
    ] = None
    date_created: Annotated[
        AwareDatetime | None,
        Field(
            alias="dateCreated",
            description="Date the collection was created",
            examples=[
                "Dates are in ISO-8601 format. Example date (January 2nd 2014 12pm UTC): 2014-01-02T12:00:00.000+0000"
            ],
        ),
    ] = None
    slug: Annotated[
        str | None,
        Field(
            description="The slug is the URL to get to this Collection",
            examples=["https://app.getguru.com/collections/:slug_goes_here"],
        ),
    ] = None
    public_cards_enabled: Annotated[bool | None, Field(alias="publicCardsEnabled")] = None
    collection_type: Annotated[
        CollectionType | None,
        Field(
            alias="collectionType",
            description="The type can be either INTERNAL or EXTERNAL.  EXTERNAL indicates that the card is from a synced Collection.",
        ),
    ] = None
    collection_stats: Annotated[
        dict[str, Any] | None,
        Field(
            alias="collectionStats",
            description="Returns an objects of stats for this collection that includes Collection Trust Score, and Card Count.",
        ),
    ] = None
    sync_verification_enabled: Annotated[bool | None, Field(alias="syncVerificationEnabled")] = None
    collection_type_detail: Annotated[
        CollectionTypeDetail | None,
        Field(
            alias="collectionTypeDetail",
            description="The type can be FRAMEWORK, ONBOARDING, USER or EXTERNAL.",
        ),
    ] = None
    home_board_slug: Annotated[str | None, Field(alias="homeBoardSlug")] = None
    boards: Annotated[int | None, Field(description="Number of boards in this Collection")] = None
    verification_interval: Annotated[int | None, Field(alias="verificationInterval")] = None
    cards: Annotated[int | None, Field(description="Number of cards in this Collection")] = None
    made_by_guru: Annotated[bool | None, Field(alias="madeByGuru")] = None
    last_synced_date: Annotated[
        AwareDatetime | None,
        Field(
            alias="lastSyncedDate",
            description="The date that the Collection was last synced from the source",
            examples=[
                "Dates are in ISO-8601 format. Example date (January 2nd 2014 12pm UTC): 2014-01-02T12:00:00.000+0000"
            ],
        ),
    ] = None
    emoji: str | None = None
    top_level_sync_location: Annotated[
        str | None,
        Field(
            alias="topLevelSyncLocation",
            description="The URL where the content of the Collection is being synced from",
        ),
    ] = None
    public_cards: Annotated[int | None, Field(alias="publicCards")] = None
    default_verification_interval: Annotated[
        int | None, Field(alias="defaultVerificationInterval")
    ] = None
    default_verification_type: Annotated[
        DefaultVerificationType | None, Field(alias="defaultVerificationType")
    ] = None
    description: Annotated[str | None, Field(description="Collection Description")] = None
    tags: Annotated[
        int | None,
        Field(description="Returns all Tag objects associated with this collection"),
    ] = None
    token: str | None = None


class ConnectionGroup(GuruModel):
    id: str | None = None
    name: str | None = None
    authorized_by: Annotated[str | None, Field(alias="authorizedBy")] = None
    created_by: Annotated[User | None, Field(alias="createdBy")] = None
    group_icon: Annotated[str | None, Field(alias="groupIcon")] = None
    sources: list[Source] | None = None


class CustomSourceConfig(SourceConfig):
    name: str | None = None
    description: str | None = None
    icon_url: Annotated[str | None, Field(alias="iconUrl")] = None
    icon_data: Annotated[str | None, Field(alias="iconData")] = None
    icon_media_type: Annotated[str | None, Field(alias="iconMediaType")] = None
    specification: SourceApplicationSpecification | None = None


class DraftCard(GuruModel):
    id: str | None = None
    content: str | None = None
    last_modified: Annotated[AwareDatetime | None, Field(alias="lastModified")] = None
    version: int | None = None
    collection: CollectionModel | None = None
    created_by: Annotated[User | None, Field(alias="createdBy")] = None
    last_modified_by: Annotated[User | None, Field(alias="lastModifiedBy")] = None
    json_content: Annotated[str | None, Field(alias="jsonContent")] = None
    card_id: Annotated[str | None, Field(alias="cardId")] = None
    created_date: Annotated[AwareDatetime | None, Field(alias="createdDate")] = None
    content_schema_version: Annotated[str | None, Field(alias="contentSchemaVersion")] = None
    card_template_id: Annotated[str | None, Field(alias="cardTemplateId")] = None
    card_version: Annotated[int | None, Field(alias="cardVersion")] = None
    scheduled_publish_date: Annotated[AwareDatetime | None, Field(alias="scheduledPublishDate")] = (
        None
    )
    user: User | None = None
    title: str | None = None


class EffectivePermissions(GuruModel):
    owner: User | None = None
    collection_access: Annotated[list[UserGroupAccess] | None, Field(alias="collectionAccess")] = (
        None
    )
    board_permissions: Annotated[list[dict[str, Any]] | None, Field(alias="boardPermissions")] = (
        None
    )
    collection_model: Annotated[CollectionModel | None, Field(alias="collectionModel")] = None
    card_collaborators: Annotated[
        list[UserGroupCollaborator] | None, Field(alias="cardCollaborators")
    ] = None


class FavoriteList(GuruModel):
    id: Annotated[
        str | None,
        Field(
            description="The ID of the favorite list",
            examples=["IDs are formatted like this: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"],
        ),
    ] = None
    last_modified: Annotated[
        AwareDatetime | None,
        Field(
            alias="lastModified",
            description="The date that the favorite list was last modified",
            examples=[
                "Dates are in ISO-8601 format. Example date (January 2nd 2014 12pm UTC): 2014-01-02T12:00:00.000+0000"
            ],
        ),
    ] = None
    default_list: Annotated[
        bool | None,
        Field(
            alias="defaultList",
            description="When this favorite list is a user's default list",
        ),
    ] = None
    items: Annotated[
        list[FavoriteListCard] | None,
        Field(description="The cards that are on the favorite list"),
    ] = None
    title: Annotated[str | None, Field(description="The title of the favorite list")] = None


class FavoriteListCard(GuruModel):
    type: str | None = None
    item_id: Annotated[str | None, Field(alias="itemId")] = None
    permissions: list[Permission] | None = None
    id: Annotated[
        str | None,
        Field(
            description="ID of the Card",
            examples=["IDs are formatted like this: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"],
        ),
    ] = None
    content: Annotated[
        str,
        Field(
            description="The Card's HTML or Markdown content",
            examples=["Here's some **awesome content**"],
        ),
    ]
    owner: Annotated[User | None, Field(description="The User object of the owner of the card")] = (
        None
    )
    last_modified: Annotated[
        AwareDatetime | None,
        Field(
            alias="lastModified",
            description="Date the Card was last modified",
            examples=[
                "Dates are in ISO-8601 format. Example date (January 2nd 2014 12pm UTC): 2014-01-02T12:00:00.000+0000"
            ],
        ),
    ] = None
    version: Annotated[
        int | None,
        Field(
            description="Current version of the Card. As the card gets updated and revised, the version number will increase.",
            examples=[1],
        ),
    ] = None
    collection: Annotated[
        CollectionModel | None, Field(description="The Collection the Card belongs to")
    ] = None
    date_created: Annotated[
        AwareDatetime | None,
        Field(
            alias="dateCreated",
            description="Date the Card was created",
            examples=[
                "Dates are in ISO-8601 format. Example date (January 2nd 2014 12pm UTC): 2014-01-02T12:00:00.000+0000"
            ],
        ),
    ] = None
    favorited_date: Annotated[
        AwareDatetime | None,
        Field(
            alias="favoritedDate",
            description="Date when this card has been favorited by the current user",
        ),
    ] = None
    slug: Annotated[
        str | None,
        Field(
            description="The slug is the URL address to the card",
            examples=["https://app.getguru.com/cards/:slug_goes_here"],
        ),
    ] = None
    last_verified: Annotated[
        AwareDatetime | None,
        Field(
            alias="lastVerified",
            description="Date the Card was last verified",
            examples=[
                "Dates are in ISO-8601 format. Example date (January 2nd 2014 12pm UTC): 2014-01-02T12:00:00.000+0000"
            ],
        ),
    ] = None
    last_verified_by: Annotated[
        User | None,
        Field(alias="lastVerifiedBy", description="The User to last verify the Card"),
    ] = None
    last_modified_by: Annotated[
        User | None,
        Field(alias="lastModifiedBy", description="The User to last modify the Card"),
    ] = None
    preferred_phrase: Annotated[
        str,
        Field(
            alias="preferredPhrase",
            description="The title of the Card",
            examples=["My New Card"],
        ),
    ]
    boards: Annotated[
        list[dict[str, Any]] | None,
        Field(description="Returns Board objects that this card appears on"),
    ] = None
    share_status: Annotated[
        ShareStatus | None,
        Field(
            alias="shareStatus",
            description="The share status of the Card.  TEAM for team shared cards and PRIVATE for privately shared cards",
            examples=["TEAM"],
        ),
    ] = None
    suppress_verification: Annotated[
        bool | None,
        Field(
            alias="suppressVerification",
            description="Flag for enabling card verification on save",
        ),
    ] = None
    verification_interval: Annotated[
        int | None,
        Field(
            alias="verificationInterval",
            description="Time interval (in days), indicating the frequency that this card needs re-verification. Passing in null will default to 30 days.",
        ),
    ] = None
    verifiers: Annotated[
        list[CardVerifier] | None,
        Field(description="Users/Groups that are responsible for verifying this card"),
    ] = None
    verification_type: Annotated[
        VerificationType | None,
        Field(
            alias="verificationType",
            description="Whether the card's verification date is ABSOLUTE or RELATIVE",
        ),
    ] = None
    collaborators: Annotated[
        list[CardCollaborator] | None,
        Field(
            description="Users/Groups that this card is explicitly shared to. Collaborators of a card are the only ones who have access if the Card's shareStatus is PRIVATE."
        ),
    ] = None
    verification_state: Annotated[
        VerificationState | None,
        Field(
            alias="verificationState",
            description="Whether the card is TRUSTED, STALE, or NEEDS_VERIFICATION",
        ),
    ] = None
    verification_reason: Annotated[
        VerificationReason | None,
        Field(
            alias="verificationReason",
            description="Reason this card needs verification.  UPDATE if this card was updated by a user that is not the verifier. NEW_VERIFIER if this card was assigned to a new verifier but has not yet been verified.  This value will only be present if the verification state is NEEDS_VERIFICATION",
        ),
    ] = None
    public_link_allowed: Annotated[bool | None, Field(alias="publicLinkAllowed")] = None
    archived: Annotated[
        bool | None, Field(description="Indicates if the Card has been archived")
    ] = None
    next_verification_date: Annotated[
        AwareDatetime | None,
        Field(
            alias="nextVerificationDate",
            description="Next date that this Card needs verification dependent on verification interval",
            examples=[
                "Dates are in ISO-8601 format. Example date (January 2nd 2014 12pm UTC): 2014-01-02T12:00:00.000+0000"
            ],
        ),
    ] = None
    original_owner: Annotated[
        User | None,
        Field(
            alias="originalOwner",
            description="The User object of the original owner of the card",
        ),
    ] = None
    last_viewed: Annotated[
        AwareDatetime | None,
        Field(
            alias="lastViewed",
            description="Last time the card was viewed",
            examples=[
                "Dates are in ISO-8601 format. Example date (January 2nd 2014 12pm UTC): 2014-01-02T12:00:00.000+0000"
            ],
        ),
    ] = None
    favorited: Annotated[
        bool | None,
        Field(description="Whether this card has been favorited by the current user"),
    ] = None
    attachments: Annotated[
        list[CardAttachment] | None, Field(description="Attachments to the card")
    ] = None
    verification_reasons: Annotated[
        list[VerificationReason] | None, Field(alias="verificationReasons")
    ] = None
    verification_initiator: Annotated[
        User | None,
        Field(
            alias="verificationInitiator",
            description="User corresponding to the action that caused the card to need verification.",
        ),
    ] = None
    comment_count: Annotated[
        int | None,
        Field(alias="commentCount", description="Number of comments on the card"),
    ] = None
    card_info: Annotated[CardInfo | None, Field(alias="cardInfo")] = None
    sync_info: Annotated[
        CardSyncInfo | None,
        Field(
            alias="syncInfo",
            description="Returns an object about Sync information, if this card is from a synced Collection. Information includes: externalUrl, lastSyncDate, lastUpdateDate, and syncType.",
        ),
    ] = None
    verification_initiation_date: Annotated[
        AwareDatetime | None,
        Field(
            alias="verificationInitiationDate",
            description="Date corresponding to the action that unverified the card",
        ),
    ] = None
    card_template_id: Annotated[
        str | None,
        Field(
            alias="cardTemplateId",
            description="ID of the template from which this card was created if applicable",
        ),
    ] = None
    folder_count: Annotated[
        int | None,
        Field(alias="folderCount", description="The number of folders this card is in"),
    ] = None
    answer_id: Annotated[str | None, Field(alias="answerId")] = None
    comments_enabled: Annotated[
        bool | None,
        Field(
            alias="commentsEnabled",
            description="A flag to indicate if comments are allowed on this Card",
        ),
    ] = None
    pending_auto_archive: Annotated[
        bool | None,
        Field(
            alias="pendingAutoArchive",
            description="A flag to indicate if this unverified card is currently in an auto archive queue",
        ),
    ] = None
    settings_update: Annotated[
        bool | None,
        Field(
            alias="settingsUpdate",
            description="A flag to indicate if the changes are only updating the settings of the card",
        ),
    ] = None
    last_verification_modified_by_type: Annotated[
        LastVerificationModifiedByType | None,
        Field(alias="lastVerificationModifiedByType"),
    ] = None
    last_verification_notes: Annotated[str | None, Field(alias="lastVerificationNotes")] = None
    last_verification_action_date: Annotated[
        AwareDatetime | None, Field(alias="lastVerificationActionDate")
    ] = None
    last_verification_confidence_score: Annotated[
        float | None, Field(alias="lastVerificationConfidenceScore")
    ] = None
    quality_check_allowed: Annotated[bool | None, Field(alias="qualityCheckAllowed")] = None
    card_type: Annotated[str | None, Field(alias="cardType")] = None
    tags: Annotated[
        list[Tag] | None,
        Field(description="Returns Tag objects associated with this card"),
    ] = None


class Folder(GuruModel):
    home: Annotated[
        bool | None,
        Field(description="Indicates if this folder is the top level folder for the collection"),
    ] = None
    id: Annotated[
        str | None,
        Field(
            description="The ID of the directory",
            examples=["IDs are formatted like this: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"],
        ),
    ] = None
    last_modified: Annotated[
        AwareDatetime | None,
        Field(
            alias="lastModified",
            description="The date that the directory was last modified",
            examples=[
                "Dates are in ISO-8601 format. Example date (January 2nd 2014 12pm UTC): 2014-01-02T12:00:00.000+0000"
            ],
        ),
    ] = None
    collection: Annotated[
        CollectionModel | None,
        Field(description="Returns the Collection object that the directory belongs to"),
    ] = None
    favorited_date: Annotated[
        AwareDatetime | None,
        Field(
            alias="favoritedDate",
            description="When this directory has been favorited by the current user",
        ),
    ] = None
    slug: Annotated[
        str | None,
        Field(
            description="The slug is the URL address to the directory",
            examples=["https://app.getguru.com/boards/:slug_goes_here"],
        ),
    ] = None
    last_modified_by: Annotated[
        User | None,
        Field(
            alias="lastModifiedBy",
            description="Returns a User object for the User who last modified the directory",
        ),
    ] = None
    favorited: Annotated[
        bool | None,
        Field(description="Whether this board has been favorited by the current user"),
    ] = None
    groups_shared_with: Annotated[
        list[str] | None,
        Field(
            alias="groupsSharedWith",
            description="Returns the groups that a directory is shared with",
        ),
    ] = None
    number_of_facts: Annotated[
        int | None,
        Field(alias="numberOfFacts", description="The number of cards in the directory"),
    ] = None
    description: Annotated[
        str | None, Field(description="An optional short description of the directory")
    ] = None
    title: Annotated[str | None, Field(description="The title of the directory")] = None


class FolderCard(FolderItem):
    id: Annotated[
        str | None,
        Field(
            description="ID of the Card",
            examples=["IDs are formatted like this: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"],
        ),
    ] = None
    permissions: list[Permission] | None = None
    content: Annotated[
        str,
        Field(
            description="The Card's HTML or Markdown content",
            examples=["Here's some **awesome content**"],
        ),
    ]
    owner: Annotated[User | None, Field(description="The User object of the owner of the card")] = (
        None
    )
    last_modified: Annotated[
        AwareDatetime | None,
        Field(
            alias="lastModified",
            description="Date the Card was last modified",
            examples=[
                "Dates are in ISO-8601 format. Example date (January 2nd 2014 12pm UTC): 2014-01-02T12:00:00.000+0000"
            ],
        ),
    ] = None
    version: Annotated[
        int | None,
        Field(
            description="Current version of the Card. As the card gets updated and revised, the version number will increase.",
            examples=[1],
        ),
    ] = None
    collection: Annotated[
        CollectionModel | None, Field(description="The Collection the Card belongs to")
    ] = None
    date_created: Annotated[
        AwareDatetime | None,
        Field(
            alias="dateCreated",
            description="Date the Card was created",
            examples=[
                "Dates are in ISO-8601 format. Example date (January 2nd 2014 12pm UTC): 2014-01-02T12:00:00.000+0000"
            ],
        ),
    ] = None
    favorited_date: Annotated[
        AwareDatetime | None,
        Field(
            alias="favoritedDate",
            description="Date when this card has been favorited by the current user",
        ),
    ] = None
    slug: Annotated[
        str | None,
        Field(
            description="The slug is the URL address to the card",
            examples=["https://app.getguru.com/cards/:slug_goes_here"],
        ),
    ] = None
    last_verified: Annotated[
        AwareDatetime | None,
        Field(
            alias="lastVerified",
            description="Date the Card was last verified",
            examples=[
                "Dates are in ISO-8601 format. Example date (January 2nd 2014 12pm UTC): 2014-01-02T12:00:00.000+0000"
            ],
        ),
    ] = None
    last_verified_by: Annotated[
        User | None,
        Field(alias="lastVerifiedBy", description="The User to last verify the Card"),
    ] = None
    last_modified_by: Annotated[
        User | None,
        Field(alias="lastModifiedBy", description="The User to last modify the Card"),
    ] = None
    preferred_phrase: Annotated[
        str,
        Field(
            alias="preferredPhrase",
            description="The title of the Card",
            examples=["My New Card"],
        ),
    ]
    boards: Annotated[
        list[dict[str, Any]] | None,
        Field(description="Returns Board objects that this card appears on"),
    ] = None
    share_status: Annotated[
        ShareStatus | None,
        Field(
            alias="shareStatus",
            description="The share status of the Card.  TEAM for team shared cards and PRIVATE for privately shared cards",
            examples=["TEAM"],
        ),
    ] = None
    suppress_verification: Annotated[
        bool | None,
        Field(
            alias="suppressVerification",
            description="Flag for enabling card verification on save",
        ),
    ] = None
    verification_interval: Annotated[
        int | None,
        Field(
            alias="verificationInterval",
            description="Time interval (in days), indicating the frequency that this card needs re-verification. Passing in null will default to 30 days.",
        ),
    ] = None
    verifiers: Annotated[
        list[CardVerifier] | None,
        Field(description="Users/Groups that are responsible for verifying this card"),
    ] = None
    verification_type: Annotated[
        VerificationType | None,
        Field(
            alias="verificationType",
            description="Whether the card's verification date is ABSOLUTE or RELATIVE",
        ),
    ] = None
    collaborators: Annotated[
        list[CardCollaborator] | None,
        Field(
            description="Users/Groups that this card is explicitly shared to. Collaborators of a card are the only ones who have access if the Card's shareStatus is PRIVATE."
        ),
    ] = None
    verification_state: Annotated[
        VerificationState | None,
        Field(
            alias="verificationState",
            description="Whether the card is TRUSTED, STALE, or NEEDS_VERIFICATION",
        ),
    ] = None
    verification_reason: Annotated[
        VerificationReason | None,
        Field(
            alias="verificationReason",
            description="Reason this card needs verification.  UPDATE if this card was updated by a user that is not the verifier. NEW_VERIFIER if this card was assigned to a new verifier but has not yet been verified.  This value will only be present if the verification state is NEEDS_VERIFICATION",
        ),
    ] = None
    public_link_allowed: Annotated[bool | None, Field(alias="publicLinkAllowed")] = None
    archived: Annotated[
        bool | None, Field(description="Indicates if the Card has been archived")
    ] = None
    next_verification_date: Annotated[
        AwareDatetime | None,
        Field(
            alias="nextVerificationDate",
            description="Next date that this Card needs verification dependent on verification interval",
            examples=[
                "Dates are in ISO-8601 format. Example date (January 2nd 2014 12pm UTC): 2014-01-02T12:00:00.000+0000"
            ],
        ),
    ] = None
    original_owner: Annotated[
        User | None,
        Field(
            alias="originalOwner",
            description="The User object of the original owner of the card",
        ),
    ] = None
    last_viewed: Annotated[
        AwareDatetime | None,
        Field(
            alias="lastViewed",
            description="Last time the card was viewed",
            examples=[
                "Dates are in ISO-8601 format. Example date (January 2nd 2014 12pm UTC): 2014-01-02T12:00:00.000+0000"
            ],
        ),
    ] = None
    favorited: Annotated[
        bool | None,
        Field(description="Whether this card has been favorited by the current user"),
    ] = None
    attachments: Annotated[
        list[CardAttachment] | None, Field(description="Attachments to the card")
    ] = None
    verification_reasons: Annotated[
        list[VerificationReason] | None, Field(alias="verificationReasons")
    ] = None
    verification_initiator: Annotated[
        User | None,
        Field(
            alias="verificationInitiator",
            description="User corresponding to the action that caused the card to need verification.",
        ),
    ] = None
    comment_count: Annotated[
        int | None,
        Field(alias="commentCount", description="Number of comments on the card"),
    ] = None
    card_info: Annotated[CardInfo | None, Field(alias="cardInfo")] = None
    sync_info: Annotated[
        CardSyncInfo | None,
        Field(
            alias="syncInfo",
            description="Returns an object about Sync information, if this card is from a synced Collection. Information includes: externalUrl, lastSyncDate, lastUpdateDate, and syncType.",
        ),
    ] = None
    verification_initiation_date: Annotated[
        AwareDatetime | None,
        Field(
            alias="verificationInitiationDate",
            description="Date corresponding to the action that unverified the card",
        ),
    ] = None
    card_template_id: Annotated[
        str | None,
        Field(
            alias="cardTemplateId",
            description="ID of the template from which this card was created if applicable",
        ),
    ] = None
    folder_count: Annotated[
        int | None,
        Field(alias="folderCount", description="The number of folders this card is in"),
    ] = None
    answer_id: Annotated[str | None, Field(alias="answerId")] = None
    comments_enabled: Annotated[
        bool | None,
        Field(
            alias="commentsEnabled",
            description="A flag to indicate if comments are allowed on this Card",
        ),
    ] = None
    pending_auto_archive: Annotated[
        bool | None,
        Field(
            alias="pendingAutoArchive",
            description="A flag to indicate if this unverified card is currently in an auto archive queue",
        ),
    ] = None
    settings_update: Annotated[
        bool | None,
        Field(
            alias="settingsUpdate",
            description="A flag to indicate if the changes are only updating the settings of the card",
        ),
    ] = None
    last_verification_modified_by_type: Annotated[
        LastVerificationModifiedByType | None,
        Field(alias="lastVerificationModifiedByType"),
    ] = None
    last_verification_notes: Annotated[str | None, Field(alias="lastVerificationNotes")] = None
    last_verification_action_date: Annotated[
        AwareDatetime | None, Field(alias="lastVerificationActionDate")
    ] = None
    last_verification_confidence_score: Annotated[
        float | None, Field(alias="lastVerificationConfidenceScore")
    ] = None
    quality_check_allowed: Annotated[bool | None, Field(alias="qualityCheckAllowed")] = None
    card_type: Annotated[str | None, Field(alias="cardType")] = None
    tags: Annotated[
        list[Tag] | None,
        Field(description="Returns Tag objects associated with this card"),
    ] = None


class GroupCollectionAccess(GuruModel):
    collection: CollectionModel | None = None
    object_role: Annotated[RoleModel | None, Field(alias="objectRole")] = None
    number_of_authors: Annotated[int | None, Field(alias="numberOfAuthors")] = None
    role: Role1 | None = None


class GroupedSourceConnection(GuruModel):
    id: str | None = None
    name: str | None = None
    source_definition: Annotated[SourceDefinition | None, Field(alias="sourceDefinition")] = None
    group_icon: Annotated[str | None, Field(alias="groupIcon")] = None
    source_count: Annotated[int | None, Field(alias="sourceCount")] = None
    connection_issues_count: Annotated[int | None, Field(alias="connectionIssuesCount")] = None
    is_single_install_only: Annotated[bool | None, Field(alias="isSingleInstallOnly")] = None
    connections: list[ConnectionGroup] | None = None


class GuruIPaasSourceConfig(SourceConfig):
    name: str | None = None
    description: str | None = None
    instance_id: Annotated[str | None, Field(alias="instanceId")] = None
    integration_id: Annotated[str | None, Field(alias="integrationId")] = None
    specification: SourceApplicationSpecification | None = None


class KnowledgeAgent(GuruModel):
    id: UUID | None = None
    name: str | None = None
    description: str | None = None
    sources: list[Source] | None = None
    collections: list[CollectionModel] | None = None
    date_created: Annotated[AwareDatetime | None, Field(alias="dateCreated")] = None
    created_by: Annotated[User | None, Field(alias="createdBy")] = None
    is_default: Annotated[bool | None, Field(alias="isDefault")] = None
    use_all_sources: Annotated[bool | None, Field(alias="useAllSources")] = None
    image_url: Annotated[str | None, Field(alias="imageUrl")] = None
    no_answer_message: Annotated[str | None, Field(alias="noAnswerMessage")] = None
    urls: list[KnowledgeAgentUrl] | None = None
    limit_slack_responses_to_all_members_content: Annotated[
        bool | None, Field(alias="limitSlackResponsesToAllMembersContent")
    ] = None
    legacy_mode: Annotated[bool | None, Field(alias="legacyMode")] = None
    allow_in_search_bar: Annotated[bool | None, Field(alias="allowInSearchBar")] = None
    tone: str | None = None
    default_system_tone: Annotated[str | None, Field(alias="defaultSystemTone")] = None
    answer_prompt: Annotated[str | None, Field(alias="answerPrompt")] = None
    default_system_answer_prompt: Annotated[
        str | None, Field(alias="defaultSystemAnswerPrompt")
    ] = None
    research_allowed: Annotated[bool | None, Field(alias="researchAllowed")] = None
    chat_allowed: Annotated[bool | None, Field(alias="chatAllowed")] = None
    color: str | None = None
    web_search_mode: Annotated[WebSearchMode | None, Field(alias="webSearchMode")] = None
    web_search_sites: Annotated[list[WebSearchSite] | None, Field(alias="webSearchSites")] = None
    permissions: list[Permission] | None = None
    verification_agent_enabled: Annotated[bool | None, Field(alias="verificationAgentEnabled")] = (
        None
    )
    filter_config: Annotated[KnowledgeAgentFilterConfig | None, Field(alias="filterConfig")] = None
    agent_type: Annotated[AgentType | None, Field(alias="agentType")] = None


class KnowledgeAgentAccess(GuruModel):
    group: UserGroup | None = None
    role: Role2 | None = None
    object_role: Annotated[RoleModel | None, Field(alias="objectRole")] = None


class KnowledgeAgentExtendedInfo(UserExtendedInfo):
    agent: KnowledgeAgent | None = None


class KnowledgeAgentQualityConfig(GuruModel):
    quality_config: Annotated[QualityConfig | None, Field(alias="qualityConfig")] = None
    verification_filter_mode: Annotated[
        VerificationFilterMode | None, Field(alias="verificationFilterMode")
    ] = None
    default_config: Annotated[QualityConfig | None, Field(alias="defaultConfig")] = None
    quality_source_scope: Annotated[
        QualitySourceScope | None, Field(alias="qualitySourceScope")
    ] = None
    quality_collections: Annotated[
        list[CollectionModel] | None, Field(alias="qualityCollections")
    ] = None
    quality_sources: Annotated[list[Source] | None, Field(alias="qualitySources")] = None


class KnowledgeAgentSkillAccess(GuruModel):
    group: UserGroup | None = None
    date_created: Annotated[AwareDatetime | None, Field(alias="dateCreated")] = None


class KnowledgeAgentUrl(GuruModel):
    id: UUID | None = None
    name: str | None = None
    url: str | None = None
    assistants: list[KnowledgeAgent] | None = None


class KnowledgeAlert(GuruModel):
    id: str | None = None
    date_created: Annotated[AwareDatetime | None, Field(alias="dateCreated")] = None
    creator: User | None = None
    card_id: Annotated[str | None, Field(alias="cardId")] = None
    scheduled_send_date: Annotated[AwareDatetime | None, Field(alias="scheduledSendDate")] = None
    suppress_notifications: Annotated[bool | None, Field(alias="suppressNotifications")] = None
    note: str | None = None
    last_manual_reminder_date: Annotated[
        AwareDatetime | None, Field(alias="lastManualReminderDate")
    ] = None
    last_automated_reminder_date: Annotated[
        AwareDatetime | None, Field(alias="lastAutomatedReminderDate")
    ] = None
    groups: list[UserGroup] | None = None


class KnowledgeAlertDelegated(GuruModel):
    card: Card | None = None
    collection_hex_color: Annotated[str | None, Field(alias="collectionHexColor")] = None
    read_count: Annotated[int | None, Field(alias="readCount")] = None
    unread_count: Annotated[int | None, Field(alias="unreadCount")] = None
    alert_id: Annotated[str | None, Field(alias="alertId")] = None
    card_title: Annotated[str | None, Field(alias="cardTitle")] = None
    date_sent: Annotated[AwareDatetime | None, Field(alias="dateSent")] = None
    scheduled_send_date: Annotated[AwareDatetime | None, Field(alias="scheduledSendDate")] = None
    percent_read: Annotated[int | None, Field(alias="percentRead")] = None
    sent_by: Annotated[User | None, Field(alias="sentBy")] = None
    note: str | None = None
    groups: list[UserGroup] | None = None


class KnowledgeAlertNotification(GuruModel):
    creator: User | None = None
    card: Card | None = None
    viewed: bool | None = None
    collection_hex_color: Annotated[str | None, Field(alias="collectionHexColor")] = None
    featured_image: Annotated[FeaturedImageCandidateEntry | None, Field(alias="featuredImage")] = (
        None
    )
    read: bool | None = None
    alert_id: Annotated[str | None, Field(alias="alertId")] = None
    card_title: Annotated[str | None, Field(alias="cardTitle")] = None
    date_sent: Annotated[AwareDatetime | None, Field(alias="dateSent")] = None
    alert_note: Annotated[str | None, Field(alias="alertNote")] = None
    groups: list[UserGroup] | None = None


class KnowledgeCenteredSupportResponse(GuruModel):
    date: AwareDatetime | None = None
    card: Card | None = None
    conversation_id: Annotated[str | None, Field(alias="conversationId")] = None
    user: User | None = None
    platform: Platform | None = None


class MentionNotification(GuruModel):
    id: str | None = None
    comment: CardComment | None = None
    creator: User | None = None
    card: Card | None = None
    viewed: bool | None = None
    date_sent: Annotated[AwareDatetime | None, Field(alias="dateSent")] = None
    mention: str | None = None
    user_task_id: Annotated[str | None, Field(alias="userTaskId")] = None
    comment_reply_id: Annotated[str | None, Field(alias="commentReplyId")] = None
    mention_source: Annotated[MentionSource | None, Field(alias="mentionSource")] = None
    draft_comment_source: Annotated[
        DraftCommentSource | None, Field(alias="draftCommentSource")
    ] = None
    draft_comment_reply_source: Annotated[
        DraftCommentReplySource | None, Field(alias="draftCommentReplySource")
    ] = None
    title: str | None = None


class NavigationPinModel(GuruModel):
    id: UUID | None = None
    object_type: Annotated[ObjectType1 | None, Field(alias="objectType")] = None
    object_id: Annotated[UUID | None, Field(alias="objectId")] = None
    object_name: Annotated[str | None, Field(alias="objectName")] = None
    scope: Scope | None = None
    metadata: PinMetadata | None = None
    visible_to: Annotated[list[UserGroup] | None, Field(alias="visibleTo")] = None


class NewCard(GuruModel):
    folder_ids: Annotated[
        list[str] | None,
        Field(
            alias="folderIds",
            description="One or more folder IDs to which the new card should be added on creation",
        ),
    ] = None
    permissions: list[Permission] | None = None
    id: Annotated[
        str | None,
        Field(
            description="ID of the Card",
            examples=["IDs are formatted like this: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"],
        ),
    ] = None
    content: Annotated[
        str,
        Field(
            description="The Card's HTML or Markdown content",
            examples=["Here's some **awesome content**"],
        ),
    ]
    owner: Annotated[User | None, Field(description="The User object of the owner of the card")] = (
        None
    )
    last_modified: Annotated[
        AwareDatetime | None,
        Field(
            alias="lastModified",
            description="Date the Card was last modified",
            examples=[
                "Dates are in ISO-8601 format. Example date (January 2nd 2014 12pm UTC): 2014-01-02T12:00:00.000+0000"
            ],
        ),
    ] = None
    version: Annotated[
        int | None,
        Field(
            description="Current version of the Card. As the card gets updated and revised, the version number will increase.",
            examples=[1],
        ),
    ] = None
    collection: Annotated[
        CollectionModel | None, Field(description="The Collection the Card belongs to")
    ] = None
    date_created: Annotated[
        AwareDatetime | None,
        Field(
            alias="dateCreated",
            description="Date the Card was created",
            examples=[
                "Dates are in ISO-8601 format. Example date (January 2nd 2014 12pm UTC): 2014-01-02T12:00:00.000+0000"
            ],
        ),
    ] = None
    favorited_date: Annotated[
        AwareDatetime | None,
        Field(
            alias="favoritedDate",
            description="Date when this card has been favorited by the current user",
        ),
    ] = None
    slug: Annotated[
        str | None,
        Field(
            description="The slug is the URL address to the card",
            examples=["https://app.getguru.com/cards/:slug_goes_here"],
        ),
    ] = None
    last_verified: Annotated[
        AwareDatetime | None,
        Field(
            alias="lastVerified",
            description="Date the Card was last verified",
            examples=[
                "Dates are in ISO-8601 format. Example date (January 2nd 2014 12pm UTC): 2014-01-02T12:00:00.000+0000"
            ],
        ),
    ] = None
    last_verified_by: Annotated[
        User | None,
        Field(alias="lastVerifiedBy", description="The User to last verify the Card"),
    ] = None
    last_modified_by: Annotated[
        User | None,
        Field(alias="lastModifiedBy", description="The User to last modify the Card"),
    ] = None
    preferred_phrase: Annotated[
        str,
        Field(
            alias="preferredPhrase",
            description="The title of the Card",
            examples=["My New Card"],
        ),
    ]
    boards: Annotated[
        list[dict[str, Any]] | None,
        Field(description="Returns Board objects that this card appears on"),
    ] = None
    share_status: Annotated[
        ShareStatus | None,
        Field(
            alias="shareStatus",
            description="The share status of the Card.  TEAM for team shared cards and PRIVATE for privately shared cards",
            examples=["TEAM"],
        ),
    ] = None
    suppress_verification: Annotated[
        bool | None,
        Field(
            alias="suppressVerification",
            description="Flag for enabling card verification on save",
        ),
    ] = None
    verification_interval: Annotated[
        int | None,
        Field(
            alias="verificationInterval",
            description="Time interval (in days), indicating the frequency that this card needs re-verification. Passing in null will default to 30 days.",
        ),
    ] = None
    verifiers: Annotated[
        list[CardVerifier] | None,
        Field(description="Users/Groups that are responsible for verifying this card"),
    ] = None
    verification_type: Annotated[
        VerificationType | None,
        Field(
            alias="verificationType",
            description="Whether the card's verification date is ABSOLUTE or RELATIVE",
        ),
    ] = None
    collaborators: Annotated[
        list[CardCollaborator] | None,
        Field(
            description="Users/Groups that this card is explicitly shared to. Collaborators of a card are the only ones who have access if the Card's shareStatus is PRIVATE."
        ),
    ] = None
    verification_state: Annotated[
        VerificationState | None,
        Field(
            alias="verificationState",
            description="Whether the card is TRUSTED, STALE, or NEEDS_VERIFICATION",
        ),
    ] = None
    verification_reason: Annotated[
        VerificationReason | None,
        Field(
            alias="verificationReason",
            description="Reason this card needs verification.  UPDATE if this card was updated by a user that is not the verifier. NEW_VERIFIER if this card was assigned to a new verifier but has not yet been verified.  This value will only be present if the verification state is NEEDS_VERIFICATION",
        ),
    ] = None
    public_link_allowed: Annotated[bool | None, Field(alias="publicLinkAllowed")] = None
    archived: Annotated[
        bool | None, Field(description="Indicates if the Card has been archived")
    ] = None
    next_verification_date: Annotated[
        AwareDatetime | None,
        Field(
            alias="nextVerificationDate",
            description="Next date that this Card needs verification dependent on verification interval",
            examples=[
                "Dates are in ISO-8601 format. Example date (January 2nd 2014 12pm UTC): 2014-01-02T12:00:00.000+0000"
            ],
        ),
    ] = None
    original_owner: Annotated[
        User | None,
        Field(
            alias="originalOwner",
            description="The User object of the original owner of the card",
        ),
    ] = None
    last_viewed: Annotated[
        AwareDatetime | None,
        Field(
            alias="lastViewed",
            description="Last time the card was viewed",
            examples=[
                "Dates are in ISO-8601 format. Example date (January 2nd 2014 12pm UTC): 2014-01-02T12:00:00.000+0000"
            ],
        ),
    ] = None
    favorited: Annotated[
        bool | None,
        Field(description="Whether this card has been favorited by the current user"),
    ] = None
    attachments: Annotated[
        list[CardAttachment] | None, Field(description="Attachments to the card")
    ] = None
    verification_reasons: Annotated[
        list[VerificationReason] | None, Field(alias="verificationReasons")
    ] = None
    verification_initiator: Annotated[
        User | None,
        Field(
            alias="verificationInitiator",
            description="User corresponding to the action that caused the card to need verification.",
        ),
    ] = None
    comment_count: Annotated[
        int | None,
        Field(alias="commentCount", description="Number of comments on the card"),
    ] = None
    card_info: Annotated[CardInfo | None, Field(alias="cardInfo")] = None
    sync_info: Annotated[
        CardSyncInfo | None,
        Field(
            alias="syncInfo",
            description="Returns an object about Sync information, if this card is from a synced Collection. Information includes: externalUrl, lastSyncDate, lastUpdateDate, and syncType.",
        ),
    ] = None
    verification_initiation_date: Annotated[
        AwareDatetime | None,
        Field(
            alias="verificationInitiationDate",
            description="Date corresponding to the action that unverified the card",
        ),
    ] = None
    card_template_id: Annotated[
        str | None,
        Field(
            alias="cardTemplateId",
            description="ID of the template from which this card was created if applicable",
        ),
    ] = None
    folder_count: Annotated[
        int | None,
        Field(alias="folderCount", description="The number of folders this card is in"),
    ] = None
    answer_id: Annotated[str | None, Field(alias="answerId")] = None
    comments_enabled: Annotated[
        bool | None,
        Field(
            alias="commentsEnabled",
            description="A flag to indicate if comments are allowed on this Card",
        ),
    ] = None
    pending_auto_archive: Annotated[
        bool | None,
        Field(
            alias="pendingAutoArchive",
            description="A flag to indicate if this unverified card is currently in an auto archive queue",
        ),
    ] = None
    settings_update: Annotated[
        bool | None,
        Field(
            alias="settingsUpdate",
            description="A flag to indicate if the changes are only updating the settings of the card",
        ),
    ] = None
    last_verification_modified_by_type: Annotated[
        LastVerificationModifiedByType | None,
        Field(alias="lastVerificationModifiedByType"),
    ] = None
    last_verification_notes: Annotated[str | None, Field(alias="lastVerificationNotes")] = None
    last_verification_action_date: Annotated[
        AwareDatetime | None, Field(alias="lastVerificationActionDate")
    ] = None
    last_verification_confidence_score: Annotated[
        float | None, Field(alias="lastVerificationConfidenceScore")
    ] = None
    quality_check_allowed: Annotated[bool | None, Field(alias="qualityCheckAllowed")] = None
    card_type: Annotated[str | None, Field(alias="cardType")] = None
    tags: Annotated[
        list[Tag] | None,
        Field(description="Returns Tag objects associated with this card"),
    ] = None


class NewFolder(GuruModel):
    prev_sibling_item_id: Annotated[
        str | None,
        Field(
            alias="prevSiblingItemId",
            description="The item id of the item after which this item should be added.  May also be 'first' or 'last' to indicate the first or last position respectively.  Defaults to 'last' if unspecified.",
        ),
    ] = None
    parent_folder_id: Annotated[str | None, Field(alias="parentFolderId")] = None
    home: Annotated[
        bool | None,
        Field(description="Indicates if this folder is the top level folder for the collection"),
    ] = None
    id: Annotated[
        str | None,
        Field(
            description="The ID of the directory",
            examples=["IDs are formatted like this: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"],
        ),
    ] = None
    last_modified: Annotated[
        AwareDatetime | None,
        Field(
            alias="lastModified",
            description="The date that the directory was last modified",
            examples=[
                "Dates are in ISO-8601 format. Example date (January 2nd 2014 12pm UTC): 2014-01-02T12:00:00.000+0000"
            ],
        ),
    ] = None
    collection: Annotated[
        CollectionModel | None,
        Field(description="Returns the Collection object that the directory belongs to"),
    ] = None
    favorited_date: Annotated[
        AwareDatetime | None,
        Field(
            alias="favoritedDate",
            description="When this directory has been favorited by the current user",
        ),
    ] = None
    slug: Annotated[
        str | None,
        Field(
            description="The slug is the URL address to the directory",
            examples=["https://app.getguru.com/boards/:slug_goes_here"],
        ),
    ] = None
    last_modified_by: Annotated[
        User | None,
        Field(
            alias="lastModifiedBy",
            description="Returns a User object for the User who last modified the directory",
        ),
    ] = None
    favorited: Annotated[
        bool | None,
        Field(description="Whether this board has been favorited by the current user"),
    ] = None
    groups_shared_with: Annotated[
        list[str] | None,
        Field(
            alias="groupsSharedWith",
            description="Returns the groups that a directory is shared with",
        ),
    ] = None
    number_of_facts: Annotated[
        int | None,
        Field(alias="numberOfFacts", description="The number of cards in the directory"),
    ] = None
    description: Annotated[
        str | None, Field(description="An optional short description of the directory")
    ] = None
    title: Annotated[str | None, Field(description="The title of the directory")] = None


class ObjectMetadata(GuruModel):
    id: str | None = None
    version: int | None = None
    object_type: Annotated[ObjectType | None, Field(alias="objectType")] = None
    external_id: Annotated[str | None, Field(alias="externalId")] = None
    modified_date: Annotated[AwareDatetime | None, Field(alias="modifiedDate")] = None
    modified_by: Annotated[User | None, Field(alias="modifiedBy")] = None
    external_checksum: Annotated[str | None, Field(alias="externalChecksum")] = None
    sync_number: Annotated[int | None, Field(alias="syncNumber")] = None


class ObjectType(GuruModel):
    name: str | None = None
    fields: list[ObjectField] | None = None
    id: str | None = None
    external_id: Annotated[str | None, Field(alias="externalId")] = None
    application: Application | None = None
    templates: ObjectTypeTemplates | None = None
    analytics_enabled: Annotated[bool | None, Field(alias="analyticsEnabled")] = None
    facets: list[ObjectFacet] | None = None
    tag_configs: Annotated[list[ObjectTagConfig] | None, Field(alias="tagConfigs")] = None
    mask_configs: Annotated[list[DataMaskConfig] | None, Field(alias="maskConfigs")] = None
    data_type: Annotated[DataType | None, Field(alias="dataType")] = None
    source_data_type: Annotated[SourceDataType | None, Field(alias="sourceDataType")] = None
    current_sync_number: Annotated[int | None, Field(alias="currentSyncNumber")] = None


class ObjectTypeTemplates(GuruModel):
    card_template: Annotated[CardTemplate | None, Field(alias="cardTemplate")] = None
    object_type_id: Annotated[str | None, Field(alias="objectTypeId")] = None
    external_url_template: Annotated[str | None, Field(alias="externalUrlTemplate")] = None
    search_template: Annotated[str | None, Field(alias="searchTemplate")] = None
    title_template: Annotated[str | None, Field(alias="titleTemplate")] = None
    external_url_template_type: Annotated[
        ExternalUrlTemplateType | None, Field(alias="externalUrlTemplateType")
    ] = None
    title_template_type: Annotated[TitleTemplateType | None, Field(alias="titleTemplateType")] = (
        None
    )
    order_by_template: Annotated[str | None, Field(alias="orderByTemplate")] = None
    order_by_template_type: Annotated[
        OrderByTemplateType | None, Field(alias="orderByTemplateType")
    ] = None
    order_by_order_type: Annotated[OrderByOrderType | None, Field(alias="orderByOrderType")] = None


class Organization(GuruModel):
    name: str | None = None
    id: str | None = None
    workspaces: list[Team] | None = None


class Page(GuruModel):
    draft_id: Annotated[
        str | None, Field(alias="draftId", description="The ID of the draft to publish")
    ] = None
    draft: Annotated[bool | None, Field(description="Indicates if this is a draft")] = None
    permissions: list[Permission] | None = None
    id: Annotated[
        str | None,
        Field(
            description="The ID of the object",
            examples=["IDs are formatted like this: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"],
        ),
    ] = None
    last_modified: Annotated[
        AwareDatetime | None,
        Field(
            alias="lastModified",
            description="The date that the object was last modified",
            examples=[
                "Dates are in ISO-8601 format. Example date (January 2nd 2014 12pm UTC): 2014-01-02T12:00:00.000+0000"
            ],
        ),
    ] = None
    team: Annotated[Team | None, Field(description="The team that the object is on")] = None
    date_created: Annotated[
        AwareDatetime | None,
        Field(
            alias="dateCreated",
            description="The date that the object was created",
            examples=[
                "Dates are in ISO-8601 format. Example date (January 2nd 2014 12pm UTC): 2014-01-02T12:00:00.000+0000"
            ],
        ),
    ] = None
    last_modified_by: Annotated[
        User | None,
        Field(alias="lastModifiedBy", description="The last user who modified the object"),
    ] = None
    json_content: Annotated[
        str | None,
        Field(alias="jsonContent", description="The json content of the page"),
    ] = None
    hero_image: Annotated[
        str | None, Field(alias="heroImage", description="The hero image link")
    ] = None
    badge_emoji: Annotated[
        str | None,
        Field(
            alias="badgeEmoji",
            description="An emoji value for the badge of the page",
            examples=[":star:"],
        ),
    ] = None
    parent_page_id: Annotated[
        str | None, Field(alias="parentPageId", description="The ID of the parent page")
    ] = None
    sub_pages: Annotated[
        list[BasePage] | None,
        Field(alias="subPages", description="An ordered list of sub-pages"),
    ] = None
    only_navigable: Annotated[
        bool | None,
        Field(
            alias="onlyNavigable",
            description="Indicates if the page is only visible for navigation purposes",
        ),
    ] = None
    knowledge_agent_id: Annotated[
        str | None,
        Field(
            alias="knowledgeAgentId",
            description="The ID of the default Knowledge Agent for this page",
        ),
    ] = None
    editable: Annotated[
        bool | None,
        Field(description="Indicates if this is editable by the current user"),
    ] = None
    title: Annotated[str | None, Field(description="The title of the page")] = None


class PermissionedObjectTag(GuruModel):
    object_type: Annotated[ObjectType | None, Field(alias="objectType")] = None
    tag_config: Annotated[ObjectTagConfig | None, Field(alias="tagConfig")] = None


class PinnedCollectionModel(GuruModel):
    position: int | None = None
    name: Annotated[str | None, Field(description="Collection Name")] = None
    read_only: Annotated[bool | None, Field(alias="readOnly")] = None
    permissions: list[Permission] | None = None
    id: Annotated[
        str | None,
        Field(
            description="ID of the collection",
            examples=["IDs are formatted like this: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"],
        ),
    ] = None
    color: Annotated[
        str | None,
        Field(
            description="A hex value for the color of the Collection",
            examples=["#f44336"],
        ),
    ] = None
    deleted: Annotated[
        bool | None,
        Field(description="Flag for whether this Collection has been deleted"),
    ] = None
    team: Team | None = None
    default_verifier: Annotated[str | None, Field(alias="defaultVerifier")] = None
    sync_type: Annotated[
        SyncType | None,
        Field(
            alias="syncType",
            description="If this Collection has been synced, this will return the type. Types include: Zendesk, Confluence, Google Drive, and Manual.",
        ),
    ] = None
    date_created: Annotated[
        AwareDatetime | None,
        Field(
            alias="dateCreated",
            description="Date the collection was created",
            examples=[
                "Dates are in ISO-8601 format. Example date (January 2nd 2014 12pm UTC): 2014-01-02T12:00:00.000+0000"
            ],
        ),
    ] = None
    slug: Annotated[
        str | None,
        Field(
            description="The slug is the URL to get to this Collection",
            examples=["https://app.getguru.com/collections/:slug_goes_here"],
        ),
    ] = None
    public_cards_enabled: Annotated[bool | None, Field(alias="publicCardsEnabled")] = None
    collection_type: Annotated[
        CollectionType | None,
        Field(
            alias="collectionType",
            description="The type can be either INTERNAL or EXTERNAL.  EXTERNAL indicates that the card is from a synced Collection.",
        ),
    ] = None
    collection_stats: Annotated[
        dict[str, Any] | None,
        Field(
            alias="collectionStats",
            description="Returns an objects of stats for this collection that includes Collection Trust Score, and Card Count.",
        ),
    ] = None
    sync_verification_enabled: Annotated[bool | None, Field(alias="syncVerificationEnabled")] = None
    collection_type_detail: Annotated[
        CollectionTypeDetail | None,
        Field(
            alias="collectionTypeDetail",
            description="The type can be FRAMEWORK, ONBOARDING, USER or EXTERNAL.",
        ),
    ] = None
    home_board_slug: Annotated[str | None, Field(alias="homeBoardSlug")] = None
    boards: Annotated[int | None, Field(description="Number of boards in this Collection")] = None
    verification_interval: Annotated[int | None, Field(alias="verificationInterval")] = None
    cards: Annotated[int | None, Field(description="Number of cards in this Collection")] = None
    made_by_guru: Annotated[bool | None, Field(alias="madeByGuru")] = None
    last_synced_date: Annotated[
        AwareDatetime | None,
        Field(
            alias="lastSyncedDate",
            description="The date that the Collection was last synced from the source",
            examples=[
                "Dates are in ISO-8601 format. Example date (January 2nd 2014 12pm UTC): 2014-01-02T12:00:00.000+0000"
            ],
        ),
    ] = None
    emoji: str | None = None
    top_level_sync_location: Annotated[
        str | None,
        Field(
            alias="topLevelSyncLocation",
            description="The URL where the content of the Collection is being synced from",
        ),
    ] = None
    public_cards: Annotated[int | None, Field(alias="publicCards")] = None
    default_verification_interval: Annotated[
        int | None, Field(alias="defaultVerificationInterval")
    ] = None
    default_verification_type: Annotated[
        DefaultVerificationType | None, Field(alias="defaultVerificationType")
    ] = None
    description: Annotated[str | None, Field(description="Collection Description")] = None
    tags: Annotated[
        int | None,
        Field(description="Returns all Tag objects associated with this collection"),
    ] = None
    token: str | None = None


class QualityAgentRun(GuruModel):
    id: Annotated[str | None, Field(description="Unique identifier for the Quality Agent run.")] = (
        None
    )
    run_date: Annotated[
        AwareDatetime | None,
        Field(alias="runDate", description="Date when the run was started."),
    ] = None
    agent: Annotated[
        KnowledgeAgent | None,
        Field(description="The Knowledge Agent associated with this run."),
    ] = None
    completion_date: Annotated[
        AwareDatetime | None,
        Field(alias="completionDate", description="Date when the run was completed."),
    ] = None
    total_documents: Annotated[
        int | None,
        Field(
            alias="totalDocuments",
            description="Total number of documents processed in this run.",
        ),
    ] = None
    verified_document_count: Annotated[
        int | None,
        Field(
            alias="verifiedDocumentCount",
            description="Number of documents verified in this run.",
        ),
    ] = None
    unverified_document_count: Annotated[
        int | None,
        Field(
            alias="unverifiedDocumentCount",
            description="Number of documents not verified in this run.",
        ),
    ] = None
    reverted_document_count: Annotated[
        int | None,
        Field(
            alias="revertedDocumentCount",
            description="Number of documents reverted in this run.",
        ),
    ] = None
    reverted_date: Annotated[
        AwareDatetime | None,
        Field(alias="revertedDate", description="Date when the run was reverted."),
    ] = None
    reverted_by: Annotated[
        User | None,
        Field(alias="revertedBy", description="The user who reverted the run."),
    ] = None


class Relationship(GuruModel):
    name: str | None = None
    id: str | None = None
    type: Type12 | None = None
    source_object_type: Annotated[ObjectType | None, Field(alias="sourceObjectType")] = None
    mapped_by: Annotated[MappedBy | None, Field(alias="mappedBy")] = None
    source_field: Annotated[ObjectField | None, Field(alias="sourceField")] = None
    source_meta_field: Annotated[SourceMetaField | None, Field(alias="sourceMetaField")] = None
    target_object_type: Annotated[ObjectType | None, Field(alias="targetObjectType")] = None
    target_field: Annotated[ObjectField | None, Field(alias="targetField")] = None
    target_meta_field: Annotated[TargetMetaField | None, Field(alias="targetMetaField")] = None


class SlackAnswerSubscription(GuruModel):
    id: UUID | None = None
    slack_channel_name: Annotated[str | None, Field(alias="slackChannelName")] = None
    slack_channel_id: Annotated[str | None, Field(alias="slackChannelId")] = None
    collections: list[CollectionModel] | None = None
    sources: list[Source] | None = None
    is_private_channel: Annotated[bool | None, Field(alias="isPrivateChannel")] = None
    assistant_id: Annotated[str | None, Field(alias="assistantId")] = None


class SlackChannelWithKnowledgeAgent(GuruModel):
    knowlege_agent: Annotated[KnowledgeAgent | None, Field(alias="knowlegeAgent")] = None
    name: str | None = None
    id: str | None = None
    private: bool | None = None
    members: list[str] | None = None
    is_archived: bool | None = None


class SlackSubscriptionChannels(GuruModel):
    available_channels: Annotated[list[SlackChannel] | None, Field(alias="availableChannels")] = (
        None
    )
    unavailable_channels: Annotated[
        list[SlackChannelWithKnowledgeAgent] | None, Field(alias="unavailableChannels")
    ] = None


class Source(GuruModel):
    name: str | None = None
    permissions: list[Permission] | None = None
    id: str | None = None
    definition: SourceDefinition | None = None
    team: Team | None = None
    application_id: Annotated[str | None, Field(alias="applicationId")] = None
    created_by: Annotated[User | None, Field(alias="createdBy")] = None
    sync_status: Annotated[SyncStatus | None, Field(alias="syncStatus")] = None
    last_synced_date: Annotated[AwareDatetime | None, Field(alias="lastSyncedDate")] = None
    source_object_types: Annotated[list[ObjectType] | None, Field(alias="sourceObjectTypes")] = None
    icon_url: Annotated[str | None, Field(alias="iconUrl")] = None
    status_reason: Annotated[StatusReason | None, Field(alias="statusReason")] = None
    last_sync_attempt: Annotated[AwareDatetime | None, Field(alias="lastSyncAttempt")] = None
    connection_id: Annotated[str | None, Field(alias="connectionId")] = None
    authorized_by: Annotated[str | None, Field(alias="authorizedBy")] = None
    connection_name: Annotated[str | None, Field(alias="connectionName")] = None
    object_syncs: Annotated[list[SourceObjectSync] | None, Field(alias="objectSyncs")] = None
    use_source_native_permissions: Annotated[
        bool | None, Field(alias="useSourceNativePermissions")
    ] = None
    merge_issues: Annotated[list[LinkedAccountIssue] | None, Field(alias="mergeIssues")] = None
    access_info: Annotated[list[UserGroupAccess] | None, Field(alias="accessInfo")] = None
    no_status_tracking: Annotated[bool | None, Field(alias="noStatusTracking")] = None
    permissioned_object_tags: Annotated[
        list[PermissionedObjectTag] | None, Field(alias="permissionedObjectTags")
    ] = None
    remote_object_syncs: Annotated[
        list[RemoteSourceObjectSync] | None, Field(alias="remoteObjectSyncs")
    ] = None
    description: str | None = None
    config: SourceConfig | None = None


class SourceApplicationSpecification(GuruModel):
    application: Application | None = None
    permissioned_object_tags: Annotated[
        list[PermissionedObjectTag] | None, Field(alias="permissionedObjectTags")
    ] = None


class SourceDocument(Document):
    source: Source | None = None
    user_allowed_to_verify: Annotated[bool | None, Field(alias="userAllowedToVerify")] = None


class SourceObjectSync(GuruModel):
    object_type: Annotated[ObjectType | None, Field(alias="objectType")] = None
    sync_status: Annotated[SyncStatus | None, Field(alias="syncStatus")] = None
    last_synced_date: Annotated[AwareDatetime | None, Field(alias="lastSyncedDate")] = None
    status_reason: Annotated[StatusReason | None, Field(alias="statusReason")] = None
    last_sync_status: Annotated[LastSyncStatus | None, Field(alias="lastSyncStatus")] = None
    last_status_reason: Annotated[LastStatusReason | None, Field(alias="lastStatusReason")] = None
    tag_config: Annotated[ObjectTagConfig | None, Field(alias="tagConfig")] = None
    last_sync_completed: Annotated[AwareDatetime | None, Field(alias="lastSyncCompleted")] = None
    object_count: Annotated[int | None, Field(alias="objectCount")] = None
    failed_object_count: Annotated[int | None, Field(alias="failedObjectCount")] = None
    indexed_percentage: Annotated[int | None, Field(alias="indexedPercentage")] = None
    last_sync_attempt: Annotated[AwareDatetime | None, Field(alias="lastSyncAttempt")] = None


class SubFolder(FolderItem):
    id: Annotated[
        str | None,
        Field(
            description="The ID of the directory",
            examples=["IDs are formatted like this: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"],
        ),
    ] = None
    home: Annotated[
        bool | None,
        Field(description="Indicates if this folder is the top level folder for the collection"),
    ] = None
    last_modified: Annotated[
        AwareDatetime | None,
        Field(
            alias="lastModified",
            description="The date that the directory was last modified",
            examples=[
                "Dates are in ISO-8601 format. Example date (January 2nd 2014 12pm UTC): 2014-01-02T12:00:00.000+0000"
            ],
        ),
    ] = None
    collection: Annotated[
        CollectionModel | None,
        Field(description="Returns the Collection object that the directory belongs to"),
    ] = None
    favorited_date: Annotated[
        AwareDatetime | None,
        Field(
            alias="favoritedDate",
            description="When this directory has been favorited by the current user",
        ),
    ] = None
    slug: Annotated[
        str | None,
        Field(
            description="The slug is the URL address to the directory",
            examples=["https://app.getguru.com/boards/:slug_goes_here"],
        ),
    ] = None
    last_modified_by: Annotated[
        User | None,
        Field(
            alias="lastModifiedBy",
            description="Returns a User object for the User who last modified the directory",
        ),
    ] = None
    favorited: Annotated[
        bool | None,
        Field(description="Whether this board has been favorited by the current user"),
    ] = None
    groups_shared_with: Annotated[
        list[str] | None,
        Field(
            alias="groupsSharedWith",
            description="Returns the groups that a directory is shared with",
        ),
    ] = None
    number_of_facts: Annotated[
        int | None,
        Field(alias="numberOfFacts", description="The number of cards in the directory"),
    ] = None
    description: Annotated[
        str | None, Field(description="An optional short description of the directory")
    ] = None
    title: Annotated[str | None, Field(description="The title of the directory")] = None


class TagCategory(GuruModel):
    name: str | None = None
    id: str | None = None
    collection: CollectionModel | None = None
    date_created: Annotated[AwareDatetime | None, Field(alias="dateCreated")] = None
    created_by: Annotated[User | None, Field(alias="createdBy")] = None
    default_category: Annotated[bool | None, Field(alias="defaultCategory")] = None
    tags: list[Tag] | None = None


class Team(GuruModel):
    name: Annotated[str | None, Field(description="Team Name")] = None
    id: Annotated[str | None, Field(description="ID of the fact")] = None
    deleted: Annotated[bool | None, Field(description="Indicates if the fact has been deleted")] = (
        None
    )
    date_created: Annotated[
        AwareDatetime | None,
        Field(
            alias="dateCreated",
            description="Date the team was created. Dates are in ISO-8601 format. Example date (January 2nd 2014 12pm UTC): 2014-01-02T12:00:00.000+0000",
        ),
    ] = None
    team_domains: Annotated[list[TeamDomain] | None, Field(alias="teamDomains")] = None
    user_role: Annotated[str | None, Field(alias="userRole")] = None
    use_case: Annotated[str | None, Field(alias="useCase")] = None
    edition: TeamEdition | None = None
    total_users: Annotated[int | None, Field(alias="totalUsers")] = None
    profile_pic_url: Annotated[str | None, Field(alias="profilePicUrl")] = None
    trial_expiration_date: Annotated[AwareDatetime | None, Field(alias="trialExpirationDate")] = (
        None
    )
    company_name: Annotated[
        str | None, Field(alias="companyName", description="Team Company Name")
    ] = None
    current_user_is_member: Annotated[bool | None, Field(alias="currentUserIsMember")] = None
    billable_users: Annotated[int | None, Field(alias="billableUsers")] = None
    slack_command_state: Annotated[str | None, Field(alias="slackCommandState")] = None
    clear_profile_pic: Annotated[bool | None, Field(alias="clearProfilePic")] = None
    default_group: Annotated[UserGroup | None, Field(alias="defaultGroup")] = None
    default_user_type: Annotated[DefaultUserType | None, Field(alias="defaultUserType")] = None
    file_sharing_disabled: Annotated[bool | None, Field(alias="fileSharingDisabled")] = None
    collection_created: Annotated[bool | None, Field(alias="collectionCreated")] = None
    team_creation_token: Annotated[str | None, Field(alias="teamCreationToken")] = None
    cards_created: Annotated[int | None, Field(alias="cardsCreated")] = None
    top_level_organization_id: Annotated[str | None, Field(alias="topLevelOrganizationId")] = None
    number_of_collections: Annotated[int | None, Field(alias="numberOfCollections")] = None
    number_of_org_shared_collections: Annotated[
        int | None, Field(alias="numberOfOrgSharedCollections")
    ] = None
    all_members_group_id: Annotated[str | None, Field(alias="allMembersGroupId")] = None
    domain: Annotated[str | None, Field(description="Domain")] = None
    description: str | None = None
    status: Status5 | None = None
    organization: Organization | None = None


class TeamUser(GuruModel):
    id: Annotated[str | None, Field(description="ID of the team member")] = None
    date_created: Annotated[AwareDatetime | None, Field(alias="dateCreated")] = None
    highest_role: Annotated[HighestRole | None, Field(alias="highestRole")] = None
    number_of_cards_as_verifier: Annotated[int | None, Field(alias="numberOfCardsAsVerifier")] = (
        None
    )
    managed_by_scim: Annotated[bool | None, Field(alias="managedByScim")] = None
    user_attributes: Annotated[dict[str, str] | None, Field(alias="userAttributes")] = None
    user: Annotated[User, Field(description="The team member")]
    groups: list[UserGroup] | None = None
    token: str | None = None


class UserGroup(GuruModel):
    name: Annotated[str | None, Field(description="Group Name")] = None
    id: Annotated[str | None, Field(description="ID of the group")] = None
    members: list[UserGroupMember] | None = None
    team: Team | None = None
    date_created: Annotated[
        AwareDatetime | None,
        Field(
            alias="dateCreated",
            description="Date the group was created. Dates are in ISO-8601 format. Example date (January 2nd 2014 12pm UTC): 2014-01-02T12:00:00.000+0000",
        ),
    ] = None
    expert_id_rank: Annotated[int | None, Field(alias="expertIdRank")] = None
    number_of_cards_as_verifier: Annotated[int | None, Field(alias="numberOfCardsAsVerifier")] = (
        None
    )
    managed_by_scim: Annotated[bool | None, Field(alias="managedByScim")] = None
    group_identifier: Annotated[str | None, Field(alias="groupIdentifier")] = None
    number_of_members: Annotated[int | None, Field(alias="numberOfMembers")] = None
    modifiable: bool | None = None
    user_modifiable: Annotated[bool | None, Field(alias="userModifiable")] = None
    single_user: Annotated[bool | None, Field(alias="singleUser")] = None
    role: Role3 | None = None


class UserGroupAccess(GuruModel):
    object_role: Annotated[RoleModel | None, Field(alias="objectRole")] = None
    group_id: Annotated[str | None, Field(alias="groupId")] = None
    role: Role4 | None = None
    group: UserGroup | None = None
    group_name: Annotated[str | None, Field(alias="groupName")] = None


class UserGroupCollaborator(CardCollaborator):
    user_group: Annotated[UserGroup | None, Field(alias="userGroup")] = None


class UserGroupVerifier(CardVerifier):
    user_group: Annotated[UserGroup | None, Field(alias="userGroup")] = None


class WhoAmI(GuruModel):
    collection: Annotated[
        CollectionModel | None,
        Field(
            description="The collection of this authenticated request, if authenticated as a collection; absent if authenticated as a user"
        ),
    ] = None
    team: Annotated[Team, Field(description="The team of the authenticated user or collection")]
    user: Annotated[
        User | None,
        Field(
            description="The user of this authenticated request, if authenticated as a user; absent if authenticated as a collection"
        ),
    ] = None
    token_type: Annotated[
        TokenType,
        Field(
            alias="tokenType",
            description="The type of token used to authenticate this request",
        ),
    ]


class WorkspacePermission(GuruModel):
    id: UUID | None = None
    group: UserGroup | None = None
    object_role: Annotated[RoleModel | None, Field(alias="objectRole")] = None


Person.model_rebuild()
AnnouncementInsightSummary.model_rebuild()
Answer.model_rebuild()
Application.model_rebuild()
AutomationPlan.model_rebuild()
BasePage.model_rebuild()
Card.model_rebuild()
CardDocument.model_rebuild()
CardTemplate.model_rebuild()
ChatThread.model_rebuild()
CollectionModel.model_rebuild()
ConnectionGroup.model_rebuild()
CustomSourceConfig.model_rebuild()
EffectivePermissions.model_rebuild()
FavoriteList.model_rebuild()
GuruIPaasSourceConfig.model_rebuild()
KnowledgeAgent.model_rebuild()
KnowledgeAgentAccess.model_rebuild()
KnowledgeAgentQualityConfig.model_rebuild()
KnowledgeAgentSkillAccess.model_rebuild()
KnowledgeAlert.model_rebuild()
KnowledgeAlertDelegated.model_rebuild()
KnowledgeAlertNotification.model_rebuild()
NavigationPinModel.model_rebuild()
ObjectMetadata.model_rebuild()
ObjectType.model_rebuild()
Organization.model_rebuild()
Page.model_rebuild()
PinnedCollectionModel.model_rebuild()
SlackAnswerSubscription.model_rebuild()
Source.model_rebuild()
Team.model_rebuild()
TeamUser.model_rebuild()
