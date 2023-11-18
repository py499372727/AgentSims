from model.model_base import ModelBase
from model.single_model_base import SingleModelBase

# class TradeItem():
#     def __int__(self):
#
#     def __repr__(self):

class TradeItemModel(ModelBase):
    '''
    Cluster methods about trading items.
    Items are designed for trading, each item belongs to an equippment.
    This class is in charge of all items in the town
    '''
    def __init__(self, app, cmd, *args,**kwargs):
        super().__init__(app, cmd)

        # todo trade 设置交易者名字 交易时间
        """
        
        tradeItem: stores specific items, recording the belonging and other status
        
        tradeItemCategories: stores information of a kind of items, and its trade records
                            trade record is meaningful for NPC's price judgement
        item config:
            [
                {"id":1,
                "name":"someThingsA","price":100,
                isExpenditure:1,
                "belongUid":uid1,
                "belongName":"XXX",
                "type":"equipment", # or 'npc', denotes the item belongs to npc or equipment
                "transaction_records":[],
                "status":""，
                "consignmentSaleUid":"", # in consignment, this key denotes where the item from
                "consignmentSaleName":"XXXX"},
                {"id":2,"name":"someThingsB","price":100},
            ]
        """
        self.tradeItems = []
        self.tradeItemCategories =[] # deprecated

    def init(self):
        for iid,item in self.app.item_configs.items():
            self.tradeItems.append(
                item
            )

    def get_id(self):
        return  1 # place holder

    # 获取所有物品信息
    def getAllTradeItems(self):
        # get information of items
        return self.tradeItems


    def getTradeItemByName(self, itemName, uid): #TODO
        # 通过所属uid/equipmentId 和物品名获取物品，可能获取到复数的物品，这个方法暂定
        for item in self.tradeItems:
            if item["name"] == itemName and item["belongUid"] == uid and item["isExpenditure"] == 0:
                return item

    def getNPCItemByItemByUid(self):
        result = []
        for item in self.tradeItems:
            if item["belongUid"] == uid and item["type"]=='npc':
                result.append(item)
        return self.returnCorrectFormat(result)

    def getTradeItemByItemId(self, itemId):
        # 通过物品id获取物品
        for item in self.tradeItems:
            if item["id"] == itemId:
                return item


    def getAllTradeItemByUid(self, uid):
        # 通过id获取所有相关物品
        result = []
        for item in self.tradeItems:
            if item["belongUid"] == uid:
                result.append(item)
        return self.returnCorrectFormat(result)

    def addTradeItem(self, item):
        self.tradeItems.append(item)

    # 物品交换, uid可以是人，也可以是物
    def exchangeTradeItem(self, fromUid, toUid, fromName, toName, itemId, actionType):
        for tradeItem in self.tradeItems:
            if tradeItem["id"] == itemId:
                tradeItem["belongUid"] = toUid
                tradeItem["belongName"] = toName
                # 设置寄卖
                if actionType == "sell":
                    tradeItem["status"] = "consignmentSale"
                    tradeItem["consignmentSaleUid"] = fromUid
                    tradeItem["consignmentSaleName"] = fromName
                    tradeItem["type"] = "equipment"

                # todo trade 设置时间
                if actionType == "buy":
                    del tradeItem["consignmentSaleUid"]
                    del tradeItem["status"]
                    # tradeItem["belongUid"] = toUid
                    # tradeItem["belongName"] = toName
                    # todo 此处type是否要把npc和player区分开？
                    tradeItem["type"] = "npc"
                    # 只有购买成功才需要记录交易日志
                    tradeItem["transaction_records"].append(
                        self.newExchangeLog(tradeItem["price"], fromUid, toUid,
                                            fromName=fromName, toName=toName, actionType=actionType) )

    # 获取寄卖物品的uid
    def getConsignmentSaleUidBYItemId(self, itemId):
        for tradeItem in self.tradeItems:
            if tradeItem["id"] == itemId:
                return tradeItem.get("consignmentSaleUid", False)

    # 创建一条交易记录
    def newExchangeLog(self, price, fromUid, toUid, fromName, toName, actionType, time):
        return {
            "price": price, "fromUid": fromUid,
            "toUid": toUid, "fromName": fromName,
            "toName": toName, "time": time
        }

    def expenditureTradeItem(self, item, uid):
        for tradeItem in self.tradeItems:
            if tradeItem["name"] == item["name"] and tradeItem["belongUid"] == uid:
                tradeItem["isExpenditure"] = 1

    def getExchangeLog(self):
        return [x["exchangeLogs"] for x in self.tradeItems]

    def getTradeItemByType(self, typeName):
        return self.returnCorrectFormat([x for x in self.tradeItems if x["type"] == typeName])

    def returnCorrectFormat(self, tradeList):
        resultList = list()
        for item in tradeList:
            newItem = dict(item)
            newItem.pop("type")
            resultList.append(newItem)
        return resultList
