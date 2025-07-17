from typing_extensions import Annotated,List,Optional
from pydantic import Field,field_validator,BaseModel
from datetime import datetime,date,timedelta
import re 

class DateTimeModel(BaseModel):
    date_time:str
    
    @field_validator("date")
    def check_datetime(cls,v):
        if not re.match(r'^\d{2}-\d{2}-\d{4} \d{2}:\d{2}$', v):
            raise ValueError("Expected format: 'DD-MM-YYYY HH:MM'")
        datetime.strptime(v, "%d-%m-%Y %H:%M")
        return v 
    
class DateModel(BaseModel):
    date:str 
    
    @field_validator("date")
    def check_date(cls,v):
        if not re.match(r'^\d{2}-\d{2}-\d{4}',v):
            raise ValueError("Expected format: 'DD-MM-YYYY")
        datetime.strptime(v, "%d-%m-%Y")
        return v
    
    
class IdentificationNumberModel(BaseModel):
    id: int 
    @field_validator("id")
    def check_format_id(cls, v):
        if not re.match(r'^\d{7,8}$', str(v)):
            raise ValueError("ID should be 7 or 8 digits")
        return v    
                
        