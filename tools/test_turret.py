# -*- coding: utf-8 -*-
"""本地 Mock 测试：不启动游戏，验证炮台的服务端逻辑。"""
import importlib.util
import os
import sys
import types

SRC = os.path.join(
    r"E:\MCStudioDownload\work\vv4u@163.com\Cpp\AddOn\bbf333789e584aeb887da1ca7da69bb6",
    "behavior_pack_2O6MJxMn", "turretScripts", "turretServerSystem.py")

# ---------- 世界状态 ----------
WORLD = {
    "bedata": {},       # (dim,pos) -> dict
    "entities": {},     # id -> {type, pos, player, dead}
    "players": {},      # playerId -> {hand: itemDict}
    "shots": [],        # 发射记录
    "kills": [],        # DestroyEntity 销毁记录
    "msgs": [],         # 聊天提示
    "exdata": {},       # ownerId -> {key: value}
    "blocks": {},       # (dim,pos) -> blockName
    "dims": {},         # entityId -> dimension
}


def _k(dim, pos):
    return (dim, pos[0], pos[1], pos[2])


class BaseSystem(object):
    def __init__(self, ns, name):
        self.ns = ns
        self.name = name

    def ListenForEvent(self, *a):
        pass


class _Pos(object):
    def __init__(self, eid):
        self.eid = eid

    def GetPos(self):
        return tuple(WORLD["entities"][self.eid]["pos"])


class _Type(object):
    def __init__(self, eid):
        self.eid = eid

    def GetEngineTypeStr(self):
        return WORLD["entities"][self.eid]["type"]

    def GetEngineType(self):
        return 0x1000 if WORLD["entities"][self.eid]["type"] != "minecraft:item" else 0x1


class _PlayerItem(object):
    def __init__(self, playerId):
        self.pid = playerId

    def _p(self):
        return WORLD["players"].setdefault(self.pid, {"hand": None, "inv": {}})

    def GetPlayerItem(self, posType, slot, getUserData=False):
        p = self._p()
        if posType == 0:                       # CARRIED
            item = p.get("hand")
        else:                                  # INVENTORY
            item = p.get("inv", {}).get(slot)
        return dict(item) if item else None

    def SetInvItemNum(self, slot, num, posType=0):
        p = self._p()
        if posType == 0:
            hand = p.get("hand")
            if hand is None:
                return False
            hand["count"] = num
            if num <= 0:
                p["hand"] = None
            return True
        inv = p.setdefault("inv", {})
        item = inv.get(slot)
        if item is None:
            return False
        item["count"] = num
        if num <= 0:
            inv.pop(slot, None)
        return True


class _ExData(object):
    def __init__(self, owner):
        self.owner = owner

    def SetExtraData(self, key, value, autoSave=True):
        WORLD["exdata"].setdefault(self.owner, {})[key] = value
        return True

    def GetExtraData(self, key):
        return WORLD["exdata"].setdefault(self.owner, {}).get(key)


class _BlockInfo(object):
    def GetBlockNew(self, pos, dim):
        name = WORLD["blocks"].get(_k(dim, pos), "minecraft:air")
        return {"name": name, "aux": 0}


class _Dimension(object):
    def __init__(self, eid):
        self.eid = eid

    def GetEntityDimensionId(self):
        return WORLD["dims"].get(self.eid, 0)


class Factory(object):
    def CreateBlockEntityData(self, lid):
        return self

    def CreateGame(self, lid):
        return self

    def CreateItem(self, eid):
        return _PlayerItem(eid)

    def CreateMsg(self, lid):
        return self

    def CreateProjectile(self, lid):
        return self

    def CreatePos(self, eid):
        return _Pos(eid)

    def CreateEngineType(self, eid):
        return _Type(eid)

    def CreateExtraData(self, owner):
        return _ExData(owner)

    def CreateBlockInfo(self, lid):
        return _BlockInfo()

    def CreateDimension(self, eid):
        return _Dimension(eid)

    # --- blockEntityData ---
    def GetBlockEntityData(self, dim, pos):
        return WORLD["bedata"].setdefault(_k(dim, pos), {})

    # --- game ---
    def GetEntitiesInSquareArea(self, eid, start, end, dim):
        out = []
        for key, e in WORLD["entities"].items():
            if e["dead"]:
                continue
            x, y, z = e["pos"]
            if not (start[0] <= x <= end[0]):
                continue
            if not (start[1] <= y <= end[1]):
                continue
            if not (start[2] <= z <= end[2]):
                continue
            out.append(key)
        return out

    # --- msg ---
    def NotifyOneMessage(self, playerId, text, color=""):
        WORLD["msgs"].append((playerId, text))
        return True

    # --- projectile ---
    def CreateProjectileEntity(self, spawnerId, identifier, param):
        WORLD["shots"].append({
            "spawner": spawnerId,
            "identifier": identifier,
            "param": dict(param),
        })
        return "proj_%d" % len(WORLD["shots"])

    # --- game ---
    def DestroyEntity(self, entityId):
        WORLD["kills"].append(entityId)
        return True


FACTORY = Factory()


class _Enum(object):
    class EntityType(object):
        Mob = 0x1000

    class ItemPosType(object):
        CARRIED = 0
        INVENTORY = 1


def _install_api():
    api = types.ModuleType("mod.server.extraServerApi")
    api.GetServerSystemCls = lambda: BaseSystem
    api.GetLevelId = lambda: "level"
    api.GetEngineCompFactory = lambda: FACTORY
    api.GetMinecraftEnum = lambda: _Enum
    api.GetEngineNamespace = lambda: "engine"
    api.GetEngineSystemName = lambda: "sys"
    api.RegisterSystem = lambda *a: None

    mod = types.ModuleType("mod")
    server = types.ModuleType("mod.server")
    mod.server = server
    server.extraServerApi = api
    sys.modules["mod"] = mod
    sys.modules["mod.server"] = server
    sys.modules["mod.server.extraServerApi"] = api


_install_api()

spec = importlib.util.spec_from_file_location("turretServerSystem", SRC)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

BLOCK = "turret:turret"
REMOTE_ITEM = "turret:remote"
DIM = 0
POS = (10, 64, 10)


def reset():
    WORLD["bedata"].clear()
    WORLD["entities"].clear()
    WORLD["players"].clear()
    WORLD["shots"].clear()
    WORLD["kills"].clear()
    WORLD["msgs"].clear()
    WORLD["exdata"].clear()
    WORLD["blocks"].clear()
    WORLD["dims"].clear()
    sysm = globals().get("sysm")
    if sysm is not None:
        sysm.trackedArrows = []   # 用例共用系统实例，同步清空箭矢跟踪


def add_entity(eid, typeStr, pos, player=False):
    WORLD["entities"][eid] = {"type": typeStr, "pos": list(pos), "player": player, "dead": False}


def setup(sysm):
    """放方块 + 加一个旁观玩家（发射需要 spawner）。"""
    sysm.OnPlaceBlockEntity({"blockName": BLOCK, "posX": POS[0], "posY": POS[1],
                             "posZ": POS[2], "dimension": DIM})
    WORLD["blocks"][_k(DIM, POS)] = BLOCK
    add_entity("p_owner", "minecraft:player", (POS[0] + 3, POS[1], POS[2]), player=True)
    WORLD["players"]["p_owner"] = {"hand": None, "inv": {}}


def tick(sysm, times=8):
    for _ in range(times):
        sysm.OnBlockEntityTick({"blockName": BLOCK, "dimension": DIM,
                                "posX": POS[0], "posY": POS[1], "posZ": POS[2]})


def right_click(sysm, playerId="p_owner"):
    sysm.useSeq += 100      # 跳过节流
    sysm.OnBlockUse({"blockName": BLOCK, "playerId": playerId, "x": POS[0], "y": POS[1],
                     "z": POS[2], "dimensionId": DIM, "cancel": False})


def bedata():
    return WORLD["bedata"][_k(DIM, POS)]


def remote_click(sysm, blockName="minecraft:stone", pos=(0, 0, 0), playerId="p_owner",
                 dim=DIM, item=REMOTE_ITEM):
    """模拟手持遥控器对方块使用；清掉节流以便连续测试。"""
    sysm.remoteGuard.pop(playerId, None)
    args = {"entityId": playerId, "itemDict": {"newItemName": item, "count": 1},
            "x": pos[0], "y": pos[1], "z": pos[2], "blockName": blockName,
            "dimensionId": dim, "ret": False}
    sysm.OnItemUseOn(args)
    return args


results = []
sysm = mod.TurretServerSystem("TurretMod", "sys")


def case(name, ok, detail=""):
    results.append((name, ok, detail))
    print(("OK   " if ok else "FAIL ") + name + ("  " + detail if detail else ""))


# ---- 用例 1：放置默认值 ----
reset()
setup(sysm)
case("放置：模式 1（警戒），ammo 字段保留默认值",
     bedata().get("ammo") == 16 and bedata().get("mode") == 1,
     "ammo=%s mode=%s" % (bedata().get("ammo"), bedata().get("mode")))

# ---- 用例 2：模式 1 锁最近的僵尸，牛不误伤 ----
reset()
setup(sysm)
add_entity("zombie_far", "minecraft:zombie", (POS[0] + 8, POS[1], POS[2]))
add_entity("zombie_near", "minecraft:zombie", (POS[0] + 4, POS[1], POS[2]))
add_entity("cow", "minecraft:cow", (POS[0] + 1, POS[1], POS[2]))
tick(sysm)
shot = WORLD["shots"][0] if WORLD["shots"] else None
ok = (shot is not None
      and shot["param"].get("targetId") == "zombie_near"
      and shot["identifier"] == "minecraft:arrow"
      and abs(shot["param"].get("damage") - 6.0) < 1e-6
      and bedata().get("ammo") == 16)
case("模式1：锁最近僵尸、不打牛、无限弹药不扣发", ok,
     "target=%s ammo=%s" % (shot and shot["param"].get("targetId"), bedata().get("ammo")))

# ---- 用例 3：弹道方向归一化 + 从炮口出发 ----
if shot:
    d = shot["param"]["direction"]
    length = (d[0] ** 2 + d[1] ** 2 + d[2] ** 2) ** 0.5
    p = shot["param"]["position"]
    ok = abs(length - 1.0) < 1e-6 and p[0] > POS[0] + 0.5 and shot["param"].get("isDamageOwner") is False
    case("弹道：方向向量归一化、炮口在朝向一侧、不伤召唤者", ok,
         "len=%.3f muzzle=(%.2f,%.2f,%.2f)" % (length, p[0], p[1], p[2]))

# ---- 用例 4：模式 1 只有牛 -> 不发射 ----
reset()
setup(sysm)
add_entity("cow", "minecraft:cow", (POS[0] + 2, POS[1], POS[2]))
tick(sysm)
case("模式1：范围内只有中立生物时不发射", len(WORLD["shots"]) == 0,
     "shots=%d" % len(WORLD["shots"]))

# ---- 用例 5：模式 2 会打牛 ----
bedata()["mode"] = 2
tick(sysm)
case("模式2：中立生物也会被打", len(WORLD["shots"]) == 1 and WORLD["shots"][0]["param"]["targetId"] == "cow",
     "shots=%d" % len(WORLD["shots"]))

# ---- 用例 6：模式 3 打玩家，模式 1 不打玩家 ----
reset()
setup(sysm)
add_entity("p_other", "minecraft:player", (POS[0] + 5, POS[1], POS[2]), player=True)
tick(sysm)
mode1_skip = len(WORLD["shots"]) == 0
bedata()["mode"] = 3
tick(sysm)
mode3_hit = len(WORLD["shots"]) == 1 and WORLD["shots"][0]["param"]["targetId"] in ("p_owner", "p_other")
case("模式1 不打玩家 / 模式3 打玩家", mode1_skip and mode3_hit,
     "mode1 shots=0:%s mode3 hit:%s" % (mode1_skip, mode3_hit))

# ---- 用例 7：超出 16 格的目标不锁 ----
reset()
setup(sysm)
add_entity("zombie_far", "minecraft:zombie", (POS[0] + 20, POS[1], POS[2]))
tick(sysm)
case("超出索敌半径的目标不锁", len(WORLD["shots"]) == 0, "shots=%d" % len(WORLD["shots"]))

# ---- 用例 8：弹药为 0 不发射 ----
reset()
setup(sysm)
bedata()["ammo"] = 0
add_entity("zombie", "minecraft:zombie", (POS[0] + 3, POS[1], POS[2]))
tick(sysm)
case("无限弹药：即使 ammo=0 也照常开火", len(WORLD["shots"]) == 1, "shots=%d" % len(WORLD["shots"]))

# ---- 用例 8b：怪打完后，场上的箭到期自动销毁 ----
reset()
setup(sysm)
add_entity("zombie", "minecraft:zombie", (POS[0] + 3, POS[1], POS[2]))
tick(sysm, times=8)
arrowId = "proj_%d" % len(WORLD["shots"])
del WORLD["entities"]["zombie"]            # 怪被打完（消失）
tick(sysm, times=100)                      # 超过 ARROW_LIFETIME=100 tick
case("怪打完后：场上的箭到期自动销毁（5 秒）",
     arrowId in WORLD["kills"] and not sysm.trackedArrows,
     "arrow=%s kills=%s" % (arrowId, WORLD["kills"]))

# ---- 用例 8c：未到期的箭不销毁 ----
reset()
setup(sysm)
add_entity("zombie", "minecraft:zombie", (POS[0] + 3, POS[1], POS[2]))
tick(sysm, times=8)
arrowId = "proj_%d" % len(WORLD["shots"])
del WORLD["entities"]["zombie"]
tick(sysm, times=8)                        # 还没到期
case("未到期的箭不会被提前销毁",
     arrowId not in WORLD["kills"] and len(sysm.trackedArrows) == 1,
     "arrow=%s kills=%s" % (arrowId, WORLD["kills"]))

# ---- 用例 9：右键循环模式 ----
reset()
setup(sysm)
seq = []
for _ in range(5):
    right_click(sysm)
    seq.append(bedata().get("mode"))
case("右键循环 1→2→3→0→1 且提示带弹药", seq == [2, 3, 0, 1, 2], "seq=%s" % (seq,))
case("提示里带弹药与模式", any(u"弹药" in m[1] for m in WORLD["msgs"]),
     WORLD["msgs"][0][1] if WORLD["msgs"] else "")

# ---- 用例 10：手持箭装填 ----
reset()
setup(sysm)
WORLD["players"]["p_owner"]["hand"] = {"newItemName": "minecraft:arrow", "count": 3}
right_click(sysm)
hand = WORLD["players"]["p_owner"]["hand"]
case("装填：弹药无限，提示且不扣箭",
     bedata().get("ammo") == 16 and hand and hand.get("count") == 3
     and any(u"无需装填" in m[1] for m in WORLD["msgs"]),
     "ammo=%s hand=%s" % (bedata().get("ammo"), hand))

# ---- 用例 11：弹药接近上限时只取需要的箭 ----
reset()
setup(sysm)
bedata()["ammo"] = 90
WORLD["players"]["p_owner"]["hand"] = {"newItemName": "minecraft:arrow", "count": 10}
right_click(sysm)
hand = WORLD["players"]["p_owner"]["hand"]
case("装填（ammo=90）：无限弹药同样提示且不扣箭",
     bedata().get("ammo") == 90 and hand and hand.get("count") == 10,
     "ammo=%s left=%s" % (bedata().get("ammo"), hand and hand.get("count")))

# ---- 用例 12：满弹时不消耗箭 ----
reset()
setup(sysm)
bedata()["ammo"] = 96
WORLD["players"]["p_owner"]["hand"] = {"newItemName": "minecraft:arrow", "count": 5}
right_click(sysm)
hand = WORLD["players"]["p_owner"]["hand"]
case("装填（ammo=96）：无限弹药同样提示且不扣箭",
     hand and hand.get("count") == 5 and any(u"无需装填" in m[1] for m in WORLD["msgs"]),
     "left=%s" % (hand and hand.get("count")))

# ---- 用例 13：附近没有玩家时不空放 ----
reset()
sysm.OnPlaceBlockEntity({"blockName": BLOCK, "posX": POS[0], "posY": POS[1],
                         "posZ": POS[2], "dimension": DIM})
add_entity("zombie", "minecraft:zombie", (POS[0] + 3, POS[1], POS[2]))
tick(sysm)
case("附近无玩家（没有 spawner）时不发射", len(WORLD["shots"]) == 0, "shots=%d" % len(WORLD["shots"]))

# ---- 用例 14：模式 0 待机 ----
reset()
setup(sysm)
bedata()["mode"] = 0
add_entity("zombie", "minecraft:zombie", (POS[0] + 3, POS[1], POS[2]))
tick(sysm)
case("模式0 待机时不索敌", len(WORLD["shots"]) == 0, "shots=%d" % len(WORLD["shots"]))

# ---- 用例 15：遥控器未绑定 ----
reset()
setup(sysm)
remote_click(sysm)
case("遥控器未绑定：提示绑定、模式不变",
     bedata().get("mode") == 1 and any(u"未绑定" in m[1] for m in WORLD["msgs"]),
     WORLD["msgs"][-1][1] if WORLD["msgs"] else "")

# ---- 用例 16：右键炮塔绑定 ----
reset()
setup(sysm)
args = remote_click(sysm, blockName=BLOCK, pos=POS)
bindVal = WORLD["exdata"].get("p_owner", {}).get("turret_remote_bind")
case("右键炮塔绑定：写入坐标、不切模式、cancel 原版使用",
     bindVal == "0,10,64,10" and bedata().get("mode") == 1 and args.get("ret") is True,
     "bind=%s mode=%s" % (bindVal, bedata().get("mode")))

# ---- 用例 17：绑定后远程切模式 ----
reset()
setup(sysm)
remote_click(sysm, blockName=BLOCK, pos=POS)
remote_click(sysm, blockName="minecraft:stone", pos=(POS[0], POS[1] - 1, POS[2]))
case("远程切模式：1→2，提示带弹药与距离",
     bedata().get("mode") == 2 and any(u"炮塔遥控" in m[1] and u"距" in m[1] for m in WORLD["msgs"]),
     WORLD["msgs"][-1][1] if WORLD["msgs"] else "")

# ---- 用例 18：超出遥控距离 ----
reset()
setup(sysm)
remote_click(sysm, blockName=BLOCK, pos=POS)
WORLD["entities"]["p_owner"]["pos"] = [POS[0] + 100, POS[1], POS[2]]
remote_click(sysm, blockName="minecraft:stone", pos=(0, 0, 0))
case("超出 64 格：拒绝执行、模式不变",
     bedata().get("mode") == 1 and any(u"超出遥控距离" in m[1] for m in WORLD["msgs"]),
     WORLD["msgs"][-1][1] if WORLD["msgs"] else "")

# ---- 用例 19：再次右键同一炮塔：弹药无限，不补弹 ----
reset()
setup(sysm)
remote_click(sysm, blockName=BLOCK, pos=POS)
WORLD["players"]["p_owner"]["inv"] = {5: {"newItemName": "minecraft:arrow", "count": 12}}
remote_click(sysm, blockName=BLOCK, pos=POS)
inv = WORLD["players"]["p_owner"]["inv"]
case("再次右键绑定炮塔：弹药无限，不扣背包箭",
     bedata().get("ammo") == 16 and inv.get(5, {}).get("count") == 12
     and any(u"无需补弹" in m[1] for m in WORLD["msgs"]),
     "ammo=%s 剩余箭=%s" % (bedata().get("ammo"), inv.get(5, {}).get("count")))

# ---- 用例 19b：无箭时同样只提示无限 ----
reset()
setup(sysm)
remote_click(sysm, blockName=BLOCK, pos=POS)
remote_click(sysm, blockName=BLOCK, pos=POS)
case("再次右键绑定炮塔：无箭时也提示弹药无限",
     bedata().get("ammo") == 16 and any(u"无需补弹" in m[1] for m in WORLD["msgs"]),
     WORLD["msgs"][-1][1] if WORLD["msgs"] else "")

# ---- 用例 20：跨维度拒绝 ----
reset()
setup(sysm)
remote_click(sysm, blockName=BLOCK, pos=POS)
WORLD["dims"]["p_owner"] = 1
remote_click(sysm, blockName="minecraft:stone", pos=(0, 0, 0))
case("跨维度：拒绝执行、模式不变",
     bedata().get("mode") == 1 and any(u"另一个维度" in m[1] for m in WORLD["msgs"]),
     WORLD["msgs"][-1][1] if WORLD["msgs"] else "")

# ---- 用例 21：目标炮塔被拆 ----
reset()
setup(sysm)
remote_click(sysm, blockName=BLOCK, pos=POS)
del WORLD["blocks"][_k(DIM, POS)]
remote_click(sysm, blockName="minecraft:stone", pos=(0, 0, 0))
case("炮塔被拆：自动解绑并提示",
     not WORLD["exdata"].get("p_owner", {}).get("turret_remote_bind")
     and any(u"不存在" in m[1] for m in WORLD["msgs"]),
     WORLD["msgs"][-1][1] if WORLD["msgs"] else "")

# ---- 用例 22：手持遥控器右键炮塔不应切模式 ----
reset()
setup(sysm)
WORLD["players"]["p_owner"]["hand"] = {"newItemName": REMOTE_ITEM, "count": 1}
right_click(sysm)
case("手持遥控器右键炮塔：不触发模式切换", bedata().get("mode") == 1 and not WORLD["msgs"],
     "mode=%s msgs=%s" % (bedata().get("mode"), len(WORLD["msgs"])))

# ---- 用例 23：非遥控器物品不响应 ----
reset()
setup(sysm)
remote_click(sysm, item="minecraft:stick")
case("手持非遥控器物品：不响应、不提示", not WORLD["msgs"], "msgs=%d" % len(WORLD["msgs"]))

passed = sum(1 for _, ok, _ in results if ok)
print("\n通过 %d/%d" % (passed, len(results)))
if passed != len(results):
    sys.exit(1)
