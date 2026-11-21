# -*- coding: utf-8 -*-
"""生成炮台模组的工程骨架：目录、manifest、方块、配方、语言文件。"""
import io
import json
import os
import uuid

ADDON_ROOT = r"E:\MCStudioDownload\work\vv4u@163.com\Cpp\AddOn"

PROJECT_ID = uuid.uuid4().hex
BP_DIR = "behavior_pack_%s" % uuid.uuid4().hex[:8]
RP_DIR = "resource_pack_%s" % uuid.uuid4().hex[:8]
ROOT = os.path.join(ADDON_ROOT, PROJECT_ID)

NAMESPACE = "turret"
BLOCK_ID = "turret:turret"


def w(path, obj):
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    if isinstance(obj, str):
        text = obj
    else:
        text = json.dumps(obj, indent=4, ensure_ascii=False) + "\n"
    io.open(full, "w", encoding="utf-8").write(text)


# ---------------- 目录 ----------------
for d in ("entities", "netease_blocks", "netease_recipes", "turretScripts"):
    os.makedirs(os.path.join(ROOT, BP_DIR, d), exist_ok=True)
for d in ("textures/blocks", "texts"):
    os.makedirs(os.path.join(ROOT, RP_DIR, d), exist_ok=True)


# ---------------- manifest ----------------
w(BP_DIR + "/manifest.json", {
    "format_version": 2,
    "header": {
        "description": "自动炮塔：自动索敌、发射追踪箭",
        "min_engine_version": [1, 18, 0],
        "name": "turret_behavior_pack",
        "uuid": str(uuid.uuid4()),
        "version": [0, 0, 1],
    },
    "modules": [{
        "type": "data",
        "uuid": str(uuid.uuid4()),
        "version": [0, 0, 1],
    }],
})

w(RP_DIR + "/manifest.json", {
    "format_version": 2,
    "header": {
        "description": "自动炮塔资源包",
        "min_engine_version": [1, 18, 0],
        "name": "turret_resource_pack",
        "uuid": str(uuid.uuid4()),
        "version": [0, 0, 1],
    },
    "modules": [{
        "type": "resources",
        "uuid": str(uuid.uuid4()),
        "version": [0, 0, 1],
    }],
})


# ---------------- 方块定义 ----------------
w(BP_DIR + "/netease_blocks/turret.json", {
    "format_version": "1.10.0",
    "minecraft:block": {
        "description": {
            "identifier": BLOCK_ID,
            "category": "construction",
        },
        "components": {
            "minecraft:destroy_time": {"value": 3.5},
            "minecraft:explosion_resistance": {"value": 12.0},
            "minecraft:block_light_absorption": {"value": 0},
            "minecraft:map_color": {"value": "#3C424B"},
            "netease:aabb": {
                "collision": {"min": [0.0, 0.0, 0.0], "max": [1.0, 1.0, 1.0]},
                "clip": {"min": [0.0, 0.0, 0.0], "max": [1.0, 1.0, 1.0]},
            },
            "netease:solid": {"value": True},
            "netease:block_entity": {"tick": True, "client_tick": False, "movable": True},
        },
    },
})

# ---------------- 配方 ----------------
w(BP_DIR + "/netease_recipes/turret_recipe.json", {
    "format_version": "1.20.10",
    "minecraft:recipe_shaped": {
        "description": {"identifier": "turret:turret_recipe"},
        "tags": ["crafting_table"],
        "pattern": ["I I", "IBI", " R "],
        "key": {
            "I": {"item": "minecraft:iron_ingot", "data": 0},
            "B": {"item": "minecraft:bow", "data": 0},
            "R": {"item": "minecraft:redstone", "data": 0},
        },
        "result": {"item": BLOCK_ID, "data": 0, "count": 1},
        "unlock": {"context": "AlwaysUnlocked"},
    },
})

# ---------------- 资源包配置 ----------------
w(RP_DIR + "/blocks.json", {
    "format_version": [1, 1, 0],
    BLOCK_ID: {
        "sound": "stone",
        "blockshape": "facing_block",
        "textures": {
            "up": "turret:turret_top",
            "down": "turret:turret_bottom",
            "north": "turret:turret_side",
            "south": "turret:turret_side",
            "east": "turret:turret_side",
            "west": "turret:turret_side",
        },
    },
})

w(RP_DIR + "/textures/terrain_texture.json", {
    "resource_pack_name": "turret",
    "texture_name": "atlas.terrain",
    "padding": 8,
    "num_mip_levels": 4,
    "texture_data": {
        "turret:turret_top": {"textures": "textures/blocks/turret_top"},
        "turret:turret_side": {"textures": "textures/blocks/turret_side"},
        "turret:turret_bottom": {"textures": "textures/blocks/turret_bottom"},
    },
})

w(RP_DIR + "/texts/zh_CN.lang", "tile.turret:turret.name=自动炮塔\n")

# ---------------- 工程根配置 ----------------
w("studio.json", {
    "Source": "空白附加包",
    "CreateVersion": "3.9.0.406366",
    "EditVersion": "3.9.0.406366",
    "OldEditCount": 0,
    "NewEditCount": 0,
    "OldComponents": [],
    "Account": "",
    "UserName": "",
    "UserId": "",
    "Id": PROJECT_ID,
    "EditType": 2,
    "IsMap": False,
    "CreateNew": True,
    "CodeEnable": True,
    "CanPublishResourceComponent": True,
    "EditName": "炮台模组",
    "GameType": 1,
    "WorldType": 1,
    "Seed": "",
    "BlockNums": [0, 0],
    "BornPoint": [0, 0, 0],
    "SaveBackMapPath": "",
    "SaveBackAddOnPath": "",
    "ResourceIds": [],
    "EditAddOnPaths": [],
    "NameSpace": NAMESPACE,
    "EditMaterialPaths": [],
    "EditLogFilePath": "",
    "ServerName": "",
    "StudioPort": 10909,
    "DCWebUrl": "https://x19apigatewayexpr.nie.netease.com",
    "ShowGuide": False,
    "AssertCacheDir": "",
    "ElkUrl": "",
    "ShowGpuDriverTips": False,
    "StudioTempPath": "",
    "EditorResourcePackPath": "",
    "EditDate": 0,
    "EditDuration": 0,
    "TestDuration": 0,
})

w("work.mcscfg", {
    "UID": PROJECT_ID,
    "Language": 0,
    "Type": 7,
    "Versions": None,
    "JavaType": 8,
    "Name": "炮台模组",
    "UpdateTime": "2026-11-14T10:40:00.0000000+08:00",
    "IconName": "",
    "Md5": None,
    "CloudMd5": None,
    "HasEncrypt": True,
    "TemplateType": 0,
    "Difficulty": 1.0,
    "Description": None,
    "CloudItemsId": None,
    "CloudItemVersion": None,
    "IsCompetive": False,
    "GameId": None,
    "VersionSubDirs": None,
    "PreComponentIds": None,
    "IsPc": True,
    "IsPreCom": False,
    "CustomWorkDir": None,
    "ImportHistoryList": None,
    "OpenEditType": 0,
    "EditMapUID": "",
    "EditMapType": 1,
    "TestMapUID": "",
    "TestJavaMapType": 0,
    "TestJavaGameVersion": "",
    "TestJavaGameMode": 0,
    "TestJavaType": 8,
    "TestBonusChest": False,
    "TestAllowCheat": True,
    "TestAlwaysDay": False,
    "TestDaylightCycle": True,
    "TestKeepInventory": True,
    "TestMobSpawn": True,
    "TestMobGriefing": True,
    "TestEntitiesDropLoot": True,
    "TestWeatherCycle": True,
    "TestCommandBlocksEnabled": True,
    "TestRandomTickSpeed": 1,
    "TestGenerateBuildings": True,
    "TestSeed": "",
    "TestCppMapType": 2,
    "TestDifficulty": 2,
    "TestCppGameMode": 1,
    "TestExperimentalHoliday": False,
    "TestExperimentalBiomes": False,
    "TestIsHardcore": False,
    "TestExperimentalModding": False,
    "TestStartWithMap": False,
    "TestRenderEngine": 0,
    "SelectComponents": [],
    "isSlim": False,
    "UseLegacyEditor": None,
    "CustomTags": [],
})

# 世界挂载的两个清单需要写包 UUID，回填
bp_manifest = json.loads(io.open(os.path.join(ROOT, BP_DIR, "manifest.json"), encoding="utf-8").read())
rp_manifest = json.loads(io.open(os.path.join(ROOT, RP_DIR, "manifest.json"), encoding="utf-8").read())
w("world_behavior_packs.json", [{
    "pack_id": bp_manifest["header"]["uuid"],
    "version": bp_manifest["header"]["version"],
}])
w("world_resource_packs.json", [{
    "pack_id": rp_manifest["header"]["uuid"],
    "version": rp_manifest["header"]["version"],
}])

print("PROJECT_ID=%s" % PROJECT_ID)
print("ROOT=%s" % ROOT)
print("BP=%s" % BP_DIR)
print("RP=%s" % RP_DIR)
