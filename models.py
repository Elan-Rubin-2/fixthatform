from cerebras.cloud.sdk import Cerebras

class CerebrasModel:
    def __init__(self,model_id,max_tokens=1024,client=Cerebras(
    # This is the default and can be omitted
    api_key='csk-xd8t5rj64mmk6j969t2hn26henttx5xc3jhh3jt9m9px8rkm'
)) -> None:
        self.client = client
        self.model_id = model_id
        self.history = []
        self.mt = max_tokens

    def getResponse(self,msg):
        self.history.append({
                            "role": "user",
                            "content": msg,
                        })
        chat_completion = self.client.chat.completions.create(
                messages=self.history,
                    max_tokens=self.mt,
                    model=self.model_id,
        )
        res = chat_completion.choices[0].message.content
        
        self.history.append({
            "role":"assistant",
            "content":res,})
        
        return res
class MedCerebrasModel(CerebrasModel):
    def __init__(self,med_schedule,model_id,client=Cerebras(
    # This is the default and can be omitted
    api_key='csk-xd8t5rj64mmk6j969t2hn26henttx5xc3jhh3jt9m9px8rkm'
)) -> None:
        super.__init__(model_id,client)
        self.med_schedule = med_schedule
        
    
