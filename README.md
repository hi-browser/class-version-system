# 基于计算机视觉的课堂考勤与行为统计系统

本项目面向智慧教学和课堂管理场景，使用 **Vue 3 + FastAPI + MySQL + YOLO** 实现课堂图片/视频上传、学生行为检测、人数统计、到课率统计、行为占比统计和可视化展示。

## 技术栈

- 前端：Vue 3、Vite、Element Plus、ECharts、Axios
- 后端：FastAPI、SQLAlchemy、MySQL、OpenCV
- 算法：Ultralytics YOLO 目标检测
- 数据集：SCB-Dataset3 YOLO 格式数据集
- 推荐环境：Windows 11、Python 3.12.x、RTX 4060、Node.js 20+

## 行为类别

本项目默认将 SCB-Dataset3 的 1-based 标签转换为 0-based 标签后使用 6 类：

| YOLO编号 | 英文名 | 中文名 |
|---|---|---|
| 0 | hand_raising | 举手互动 |
| 1 | reading | 阅读/看书 |
| 2 | writing | 低头书写 |
| 3 | using_phone | 使用手机 |
| 4 | bowing_head | 低头状态 |
| 5 | leaning_over_table | 趴桌/疑似睡觉 |

> 注意：如果你的原始标签确实是 1~6，需要先运行 `train/convert_labels_1_to_0.py` 转换标签。不要在原始数据集上直接覆盖，脚本默认会复制到新目录。

## 快速启动

### 1. 后端环境

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

如果使用 RTX 4060 GPU，建议先按 PyTorch 官网选择 CUDA 版本安装 torch，然后再安装 requirements。

复制配置：

```bash
copy .env.example .env
```

修改 `.env` 中的 MySQL 用户名、密码和数据库名。

初始化数据库：

```bash
mysql -u root -p < ../database/classroom_vision.sql
```

启动后端：

```bash
python run.py
```

访问：

```text
http://127.0.0.1:8000/docs
```

### 2. 前端环境

```bash
cd frontend
npm install
npm run dev
```

访问：

```text
http://127.0.0.1:5173
```

### 3. 数据集处理和训练

统计原始标签：

```bash
python train/check_yolo_labels.py --labels "D:/BaiduNetdiskDownload/SCB-Dataset3 yolo dataset/0.355k_university_yolo_Dataset/labels"
```

如果输出类别是 1~6，转换为 0~5：

```bash
python train/convert_labels_1_to_0.py ^
  --src "D:/BaiduNetdiskDownload/SCB-Dataset3 yolo dataset/0.355k_university_yolo_Dataset" ^
  --dst "D:/datasets/scb_0.355k_converted"
```

训练：

```bash
yolo detect train model=yolo11n.pt data=D:/datasets/scb_0.355k_converted/scb_dataset3.yaml epochs=80 imgsz=640 batch=8 device=0
```

训练完成后，将最优权重复制到：

```text
backend/weights/scb_yolo.pt
```

## 交付说明

本项目包含完整工程框架、后端 API、前端页面、数据库脚本、训练脚本、标签转换脚本和说明文档。模型权重需要你们使用准备好的 SCB 数据集训练后放入 `backend/weights/scb_yolo.pt`。
