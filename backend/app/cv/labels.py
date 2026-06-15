# SCB-Dataset3 标签从 1 开始时，训练前需要转换为 0 开始。
# 训练和系统推理统一使用 0~5。

CLASS_NAMES = {
    0: "hand_raising",
    1: "reading",
    2: "writing",
    3: "using_phone",
    4: "bowing_head",
    5: "leaning_over_table",
}

CLASS_CN = {
    0: "举手互动",
    1: "阅读/看书",
    2: "低头书写",
    3: "使用手机",
    4: "低头状态",
    5: "趴桌/疑似睡觉",
}

POSITIVE_CLASSES = {0, 1, 2}
ABNORMAL_CLASSES = {3, 4, 5}
PHONE_CLASSES = {3}
HEAD_DOWN_CLASSES = {4, 5}
