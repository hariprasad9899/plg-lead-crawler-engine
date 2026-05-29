from app.core.exceptions.base import AppException
from app.infrastructure.database.repositories.intent_repository import IntentRepo
from app.core.schemas.intents_schemas import IntentJobCreate, CreateIntentJobsRequest, CreateIntentJobsResponse
from dataclasses import asdict


class IntentService():
    def __init__(
        self,
        intent_repo: IntentRepo
    ):
        self.intent_repo = intent_repo
    
    def create_intent(self,intent_data:CreateIntentJobsRequest) -> CreateIntentJobsResponse:
        try:
            intent_job_data = IntentJobCreate(**intent_data.model_dump())
            intent_job = self.intent_repo.create_intent(data=intent_job_data)
            self.intent_repo.db.commit()
            res_data = CreateIntentJobsResponse.model_validate(intent_job)
            return res_data
        except  Exception:
            self.intent_repo.db.rollback()
            raise




    

    