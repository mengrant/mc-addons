# -*- coding: utf-8 -*-
"""本地 Mock 测试：不启动游戏，验证四方向传送带的服务端逻辑。"""
import importlib.util
import os
import sys
import types

SRC = os.path.join(
    r"E:\MCStudioDownload\work\vv4u@163.com\Cpp\AddOn\5c73955f25334332a81ffd8dec4e960a",
    "behavior_pack_sFnPdk6A", "conveyorScripts", "conveyorServerSystem.py")

# ---------- 世界状态 ----------
WORLD = {
    "blocks": {},      # (dim,x,y,z) -> name
    "containers": {},  # (dim,x,y,z) -> [slot dicts]
    "entities": {},    # entityId -> dict(type, foot, motion, dead)
}


class BaseSystem(object):
    def __init__(self, ns, name):
        self.ns = ns
        self.name = name

    def ListenForEvent(self, *a):
        pass

    def DestroyEntity(self, eid):
        WORLD["entities"][eid]["dead"] = True
        return True


class Factory(object):
    def CreateBlockInfo(self, lid):
        return self

    def CreateBlockEntityData(self, lid):
        return self

    def CreateGame(self, lid):
        return self

    def CreateItem(self, lid):
        return self

    def CreateMsg(self, lid):
        return self

    def CreatePos(self, eid):
        return _sub(self, WORLD["entities"][eid])

    def CreateActorMotion(self, eid):
        return _sub(self, WORLD["entities"][eid])

    def CreateEngineType(self, eid):
        return _sub(self, WORLD["entities"][eid])

    # --- blockInfo ---
    def GetBlockNew(self, pos, dim):
        name = WORLD["blocks"].get(_k(dim, pos))
        return {"name": name, "aux": 0} if name else None

    # --- blockEntityData ---
    def GetBlockEntityData(self, dim, pos):
        return WORLD.setdefault("bedata", {}).setdefault(_k(dim, pos), {})

    # --- game ---
    def GetEntitiesInSquareArea(self, eid, start, end, dim):
        out = []
        for eid2, e in WORLD["entities"].items():
            if e["dead"]:
                continue
            fx, fy, fz = e["foot"]
            if not (start[0] - 0.3 <= fx <= end[0] + 0.3):
                continue
            if not (start[2] - 0.3 <= fz <= end[2] + 0.3):
                continue
            if fy + 0.25 < start[1] or fy > end[1]:
                continue
            out.append(eid2)
        return out

    # --- pos / motion / type ---
    def GetFootPos(self):
        return tuple(self._e["foot"])

    def SetFootPos(self, p):
        self._e["foot"] = list(p)

    def GetMotion(self):
        return tuple(self._e["motion"])

    def SetMotion(self, m):
        self._e["motion"] = list(m)

    def GetEngineTypeStr(self):
        return self._e["type"]

    # --- item ---
    def GetDroppedItem(self, eid):
        return WORLD["entities"][eid].get("item")

    def GetContainerSize(self, pos, dim):
        slots = WORLD["containers"].get(_k(dim, pos))
        return len(slots) if slots is not None else -1

    def GetContainerItem(self, pos, slot, dim):
        slots = WORLD["containers"].get(_k(dim, pos))
        return slots[slot] if slots else None

    def SpawnItemToContainer(self, itemDict, slot, pos, dim):
        slots = WORLD["containers"].get(_k(dim, pos))
        if not slots:
            return False
        slots[slot] = dict(itemDict)
        return True


class _sub(object):
    def __init__(self, factory, entity):
        self._f = factory
        self._e = entity

    def __getattr__(self, name):
        attr = getattr(self._f, name)
        # 把工厂方法重新绑定到本代理，使方法内部的 self._e 指向具体实体
        if callable(attr) and getattr(attr, "__self__", None) is self._f:
            return types.MethodType(attr.__func__, self)
        return attr


def _k(dim, pos):
    return (dim, pos[0], pos[1], pos[2])


def _install_modules():
    for name in ("mod", "mod.common", "mod.common.mod", "mod.server", "mod.server.extraServerApi"):
        sys.modules.setdefault(name, types.ModuleType(name))
    sys.modules["mod.common.mod"].Mod = object
    sys.modules["mod"].common = sys.modules["mod.common"]
    api = sys.modules["mod.server.extraServerApi"]
    api.GetLevelId = lambda: "level"
    api.GetEngineCompFactory = lambda: Factory()
    api.GetServerSystemCls = lambda: BaseSystem
    api.GetEngineNamespace = lambda: "engine"
    api.GetEngineSystemName = lambda: "engineSys"


def load_module():
    spec = importlib.util.spec_from_file_location("conveyorServerSystem", SRC)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def reset_world(hopper_slots=5, container_pos=(0, 9, 0)):
    WORLD["blocks"].clear()
    WORLD["containers"].clear()
    WORLD["entities"].clear()
    WORLD.pop("bedata", None)
    WORLD["containers"][_k(0, container_pos)] = [None] * hopper_slots
    return WORLD["containers"][_k(0, container_pos)]


_install_modules()
mod = load_module()

results = []
BELT = (0, 10, 0)


def tick(sysm, name, pos=BELT, times=8):
    for _ in range(times):
        sysm.OnBlockEntityTick({"blockName": name, "dimension": 0,
                                "posX": pos[0], "posY": pos[1], "posZ": pos[2]})


# ---- 用例 1：四个方块方向表 ----
assert mod.BLOCK_DIRS["conveyor:belt_north"] == (0.0, -1.0)
assert mod.BLOCK_DIRS["conveyor:belt_south"] == (0.0, 1.0)
assert mod.BLOCK_DIRS["conveyor:belt_east"] == (1.0, 0.0)
assert mod.BLOCK_DIRS["conveyor:belt_west"] == (-1.0, 0.0)
results.append("四方向映射 北/南/东/西 -> OK")

# ---- 用例 2：每种方块推送方向都正确 ----
expect = {
    "conveyor:belt_north": (0.0, -1.0),
    "conveyor:belt_south": (0.0, 1.0),
    "conveyor:belt_east": (1.0, 0.0),
    "conveyor:belt_west": (-1.0, 0.0),
}
for name, (ex, ez) in expect.items():
    reset_world()
    WORLD["blocks"][_k(0, BELT)] = name
    WORLD["entities"]["e"] = {
        "type": "minecraft:pig", "foot": [0.5, 10.5, 0.5],
        "motion": [0.0, 0.0, 0.0], "dead": False,
    }
    s = mod.ConveyorServerSystem("ConveyorMod", "s_" + name)
    tick(s, name, times=10)
    vx, vz = WORLD["entities"]["e"]["motion"][0], WORLD["entities"]["e"]["motion"][2]
    assert abs(vx - ex * 0.10) < 1e-6 and abs(vz - ez * 0.10) < 1e-6, (name, vx, vz)
results.append("四方块实际推力方向 1 档 = 0.10 -> OK")

# ---- 用例 3：掉落物经传送带送入正下方漏斗 ----
hopper_pos = (0, 9, 0)
reset_world(hopper_slots=5, container_pos=hopper_pos)
WORLD["blocks"][_k(0, BELT)] = "conveyor:belt_north"
WORLD["blocks"][_k(0, hopper_pos)] = "minecraft:hopper"
WORLD["entities"]["item1"] = {
    "type": "minecraft:item", "item": {"itemName": "minecraft:iron_ingot", "count": 3},
    "foot": [0.5, 10.62, 0.5], "motion": [0.0, 0.0, 0.0], "dead": False,
}
sysm = mod.ConveyorServerSystem("ConveyorMod", "sysA")
tick(sysm, "conveyor:belt_north", times=6)
slots = WORLD["containers"][_k(0, hopper_pos)]
assert slots[0] and slots[0]["itemName"] == "minecraft:iron_ingot", slots
assert WORLD["entities"]["item1"]["dead"] is True
results.append("掉落物 -> 漏斗0号槽 入库并销毁实体 -> OK (%s x%d)" % (
    slots[0]["itemName"], slots[0]["count"]))

# ---- 用例 4：漏斗满时物品留在带上、不入格 ----
full = reset_world(hopper_slots=5, container_pos=hopper_pos)
WORLD["blocks"][_k(0, BELT)] = "conveyor:belt_north"
WORLD["blocks"][_k(0, hopper_pos)] = "minecraft:hopper"
for i in range(5):
    full[i] = {"itemName": "minecraft:stone", "count": 64}
WORLD["entities"]["item2"] = {
    "type": "minecraft:item", "item": {"itemName": "minecraft:diamond", "count": 1},
    "foot": [0.5, 10.62, 0.5], "motion": [0.0, 0.0, 0.0], "dead": False,
}
sysm2 = mod.ConveyorServerSystem("ConveyorMod", "sysB")
tick(sysm2, "conveyor:belt_north", times=4)
assert all(s["itemName"] == "minecraft:stone" for s in full), full
assert WORLD["entities"]["item2"]["dead"] is False
assert WORLD["entities"]["item2"]["motion"] != [0.0, 0.0, 0.0]
results.append("漏斗已满：物品未被覆盖、留在带上继续被推 -> OK")

# ---- 用例 5：东向带推动 +X 且向中线吸附 ----
reset_world()
WORLD["blocks"][_k(0, BELT)] = "conveyor:belt_east"
WORLD["entities"]["item3"] = {
    "type": "minecraft:item", "item": {"itemName": "minecraft:cobblestone", "count": 1},
    "foot": [0.5, 10.62, 0.22], "motion": [0.0, 0.0, 0.0], "dead": False,
}
sysm3 = mod.ConveyorServerSystem("ConveyorMod", "sysC")
tick(sysm3, "conveyor:belt_east", times=8)
e = WORLD["entities"]["item3"]
vx, vz = e["motion"][0], e["motion"][2]
assert vx > 0, "东向带应沿 +X 推动，实际 %s" % (e["motion"],)
assert abs(vz) > 0, "应有横向回正速度，实际 %s" % (e["motion"],)
assert abs(e["foot"][2] - 0.5) < 0.22, "位置应被拉向中线，实际 %s" % (e["foot"],)
results.append("东向带：+X 推送 + 中线回正 -> OK (v=%.3f, z=%.3f)" % (vx, e["foot"][2]))

# ---- 用例 6：正前方是实心方块时不推动 ----
reset_world()
WORLD["blocks"][_k(0, BELT)] = "conveyor:belt_east"
WORLD["blocks"][_k(0, (1, 10, 0))] = "minecraft:stone"
WORLD["entities"]["mob1"] = {
    "type": "minecraft:pig", "foot": [0.5, 10.5, 0.5], "motion": [0.0, 0.0, 0.0], "dead": False,
}
sysm4 = mod.ConveyorServerSystem("ConveyorMod", "sysD")
tick(sysm4, "conveyor:belt_east", times=6)
assert WORLD["entities"]["mob1"]["motion"] == [0.0, 0.0, 0.0], WORLD["entities"]["mob1"]["motion"]
results.append("正前方为实心方块：不再推动 -> OK")

# ---- 用例 7：前方是任意方向传送带不算挡道（可拐弯接力） ----
reset_world()
WORLD["blocks"][_k(0, BELT)] = "conveyor:belt_east"
WORLD["blocks"][_k(0, (1, 10, 0))] = "conveyor:belt_north"
WORLD["entities"]["mob2"] = {
    "type": "minecraft:pig", "foot": [0.5, 10.5, 0.5], "motion": [0.0, 0.0, 0.0], "dead": False,
}
sysm5 = mod.ConveyorServerSystem("ConveyorMod", "sysE")
tick(sysm5, "conveyor:belt_east", times=6)
assert WORLD["entities"]["mob2"]["motion"][0] > 0, WORLD["entities"]["mob2"]["motion"]
results.append("前方为另一条传送带：照常推动（可拐弯）-> OK")

# ---- 用例 8：右键档位循环 + 拦截原版交互 ----
reset_world()
WORLD["blocks"][_k(0, BELT)] = "conveyor:belt_north"
sysm6 = mod.ConveyorServerSystem("ConveyorMod", "sysF")
seen = []
for i in range(9):
    if i:
        sysm6.useSeq += mod.USE_THROTTLE - 1
    args = {"blockName": "conveyor:belt_north", "playerId": "p1", "x": 0, "y": 10, "z": 0,
            "dimensionId": 0}
    sysm6.OnBlockUse(args)
    assert args["cancel"] is True
    seen.append(sysm6._readLevel(0, BELT))
assert seen == [2, 3, 0, 1, 2, 3, 0, 1, 2], seen
results.append("右键档位循环 %s -> OK（含 cancel=True）" % seen)

print("全部通过：")
for r in results:
    print(" -", r)
