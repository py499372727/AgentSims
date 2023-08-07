from model.single_model_base import SingleModelBase


class NPCsModel(SingleModelBase):
    def __init__(self, app, cmd, id):
        super().__init__(app, cmd, id)

        # [{id: id, name: name}]
        self.npcs = None
        # ORM mapping.
        self.orm['npcs'] = SingleModelBase.OBJECT

    def init(self):
        self.npcs = list()

    def total(self):
        return len(self.npcs)
    
    def add_npc(self, npc_info):
        self.npcs.append(npc_info)
    
    def get_uids(self):
        return [x["id"] for x in self.npcs]
