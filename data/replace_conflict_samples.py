# -*- coding: utf-8 -*-
"""替换训练数据与金标准中的构造冲突样本（2026-08-19），用户确认替换。"""
import json
from pathlib import Path

BASE = Path(__file__).parent


def find_refusal_file(data_dir: Path) -> Path:
    for f in data_dir.glob("alpaca_*_60.json"):
        arr = json.loads(f.read_text(encoding="utf-8"))
        if any(x["input"] == "" for x in arr):
            return f
    raise FileNotFoundError("未找到拒答文件")


NEW_REFUSAL_ENTRIES = [
    {"instruction": "全国碳市场2026年的配额分配方案是什么？", "input": "", "output": "检索片段中未提供2026年配额分配方案信息，无法回答。需要补充配额分配文件。资料不足，无法完整回答。"},
    {"instruction": "绿色建筑运行评价报告的模板在哪里下载？", "input": "", "output": "检索片段中未提供报告模板信息，无法回答。需要补充模板下载渠道。资料不足，无法完整回答。"},
    {"instruction": "光伏建筑一体化项目的并网流程是什么？", "input": "", "output": "检索片段中未提供并网流程信息，无法回答。需要补充并网管理规定。资料不足，无法完整回答。"},
    {"instruction": "建筑碳足迹核算的边界设定细则有哪些？", "input": "", "output": "检索片段中未提供边界设定细则，无法回答。需要补充碳足迹核算标准。资料不足，无法完整回答。"},
    {"instruction": "近零能耗建筑技术标准的认证机构有哪些？", "input": "", "output": "检索片段中未提供认证机构名单，无法回答。需要补充认证机构名录。资料不足，无法完整回答。"},
    {"instruction": "企业温室气体排放报告的上报截止日期是什么？", "input": "", "output": "检索片段中未提供上报截止日期，无法回答。需要补充报告管理规定。资料不足，无法完整回答。"},
    {"instruction": "绿色建材标识的申请材料清单是什么？", "input": "", "output": "检索片段中未提供申请材料清单，无法回答。需要补充标识管理办法。资料不足，无法完整回答。"},
    {"instruction": "碳达峰试点城市名单在哪里查？", "input": "", "output": "检索片段中未提供试点城市名单，无法回答。需要补充试点名单文件。资料不足，无法完整回答。"},
    {"instruction": "绿色建筑星级标识的有效期是几年？", "input": "", "output": "检索片段中未提供标识有效期信息，无法回答。需要补充标识管理办法。资料不足，无法完整回答。"},
    {"instruction": "双碳目标下建筑行业的具体减排路径图是什么？", "input": "", "output": "检索片段中未提供建筑行业减排路径图，无法回答。需要补充行业行动方案。资料不足，无法完整回答。"},
    {"instruction": "碳排放配额的市场价格是如何形成的？", "input": "[证据1] 全国碳市场交易产品为碳排放配额，重点排放单位须在履约周期内清缴与自身经核查排放量相当的配额。", "output": "片段仅说明配额清缴义务，未提供价格形成机制信息。需要补充市场交易规则。资料不足，无法完整回答。"},
    {"instruction": "绿色建筑项目如何申请财政补贴？", "input": "[证据1] 绿色建筑等级分为基本级、一星级、二星级、三星级4个等级。", "output": "片段仅说明绿色建筑等级划分，未提供财政补贴申请信息。需要补充地方补贴政策。资料不足，无法完整回答。"},
    {"instruction": "近零能耗建筑如何组织验收？", "input": "[证据1] 按《近零能耗建筑技术标准》GB/T 51350-2019，建筑分为超低能耗建筑、近零能耗建筑、零能耗建筑三个层级。", "output": "片段仅说明建筑层级划分，未提供验收流程。需要补充验收技术规程。资料不足，无法完整回答。"},
    {"instruction": "全国碳市场的交易手续费是多少？", "input": "[证据1] 2021年7月16日，全国碳排放权交易市场启动上线交易，发电行业成为首个纳入全国碳市场的行业。", "output": "片段仅说明碳市场启动情况，未提供交易手续费信息。需要补充交易规则。资料不足，无法完整回答。"},
    {"instruction": "温室气体排放核查报告的格式是什么？", "input": "[证据1] 核算应遵循相关性、完整性、一致性、准确性、透明性原则。", "output": "片段仅说明核算原则，未提供核查报告格式。需要补充报告模板与规范。资料不足，无法完整回答。"},
    {"instruction": "绿色建材有哪些认证等级？", "input": "[证据1] 绿色建材是在全生命周期内减少对自然资源消耗和生态环境影响的建材产品。", "output": "片段仅说明绿色建材定义，未提供认证等级信息。需要补充认证管理办法。资料不足，无法完整回答。"},
    {"instruction": "碳达峰十大行动的牵头部门有哪些？", "input": "[证据1] 碳达峰十大行动包括能源绿色低碳转型、节能降碳增效、工业领域碳达峰等。", "output": "片段仅列出十大行动名称，未提供牵头部门分工。需要补充行动方案细则。资料不足，无法完整回答。"},
    {"instruction": "绿色建筑评价的费用由谁承担？", "input": "[证据1] 绿色建筑评价总得分分别达到60分、70分、85分时，对应一星级、二星级、三星级。", "output": "片段仅说明星级得分门槛，未提供评价费用承担方式。需要补充评价收费规则。资料不足，无法完整回答。"},
    {"instruction": "排放因子多久更新一次？", "input": "[证据1] 排放因子是表征单位生产或消费活动量的温室气体排放的系数。", "output": "片段仅说明排放因子定义，未提供更新频率。需要补充排放因子数据库说明。资料不足，无法完整回答。"},
    {"instruction": "装配式建筑有哪些结构体系可选？", "input": "[证据1] 装配式建筑是指由预制部品部件在工地装配而成的建筑。", "output": "片段仅说明装配式建筑定义，未提供结构体系选项。需要补充装配式建筑技术标准。资料不足，无法完整回答。"},
]


NEW_GOLDEN_ENTRIES = [
    {"id": "G034", "capability": "资料不足拒答", "instruction": "全国碳市场2026年的配额分配方案是什么？", "input": "", "expected": "检索片段中未提供2026年配额分配方案信息；需要补充配额分配文件。资料不足，无法完整回答。", "requires_caution": True, "note": "无召回，必须拒答"},
    {"id": "G035", "capability": "资料不足拒答", "instruction": "绿色建筑项目如何申请财政补贴？", "input": "[证据1] 绿色建筑等级分为基本级、一星级、二星级、三星级4个等级。", "expected": "片段仅说明绿色建筑等级划分，未提供财政补贴申请信息；需要补充地方补贴政策。资料不足，无法完整回答。", "requires_caution": True, "note": "弱相关片段，必须拒答"},
    {"id": "G036", "capability": "资料不足拒答", "instruction": "近零能耗建筑如何组织验收？", "input": "", "expected": "检索片段中未提供验收流程；需要补充验收技术规程。资料不足，无法完整回答。", "requires_caution": True, "note": "无召回，必须拒答"},
]


def replace_refusal(data_dir: Path) -> None:
    path = find_refusal_file(data_dir)
    items = json.loads(path.read_text(encoding="utf-8"))
    conflicts = [x for x in items if "表述不一致" in x["output"]]
    assert len(conflicts) == 20, f"冲突样本数应为20，实际 {len(conflicts)}"
    items = [x for x in items if "表述不一致" not in x["output"]]
    assert len(items) == 40
    items.extend(NEW_REFUSAL_ENTRIES)
    assert len(items) == 60
    assert all("表述不一致" not in x["output"] for x in items)
    path.write_text(json.dumps(items, ensure_ascii=False), encoding="utf-8")
    print(f"拒答层替换完成：{path.name} 60 条，无冲突样本")


def replace_golden(eval_dir: Path) -> None:
    path = eval_dir / "golden_eval.json"
    gold = json.loads(path.read_text(encoding="utf-8"))
    gconf = [x for x in gold if "表述不一致" in x["expected"]]
    assert len(gconf) == 3, [x["id"] for x in gconf]
    gold = [x for x in gold if "表述不一致" not in x["expected"]]
    gold.extend(NEW_GOLDEN_ENTRIES)
    assert len(gold) == 50
    assert all("表述不一致" not in x["expected"] for x in gold)
    path.write_text(json.dumps(gold, ensure_ascii=False, indent=2), encoding="utf-8")
    print("金标准替换完成：50 条，无冲突样本")


def main() -> None:
    replace_refusal(BASE)
    replace_golden(BASE.parent / "eval")


if __name__ == "__main__":
    main()
