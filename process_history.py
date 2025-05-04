""""
本代码用于整理文本信息，使得轨迹被转化为os gensis的格式,并且完成坐标规则化.os gensis的格式如下：
{"id": "aw_stage1_task1_1", "image": "4e511f56-33f9-49bd-8138-ceb5552412d6.png", "conversations": [{"from": "human", "value": "<image>\nYou are a GUI task expert, I will provide you with a high-level instruction, an action history, a screenshot with its corresponding accessibility tree.\n\nHigh-level instruction: Set a task due date to any date in November 2023 within the Tasks app.\n\nAction history: \n\nAccessibility tree: {\"com.google.android.apps.nexuslauncher\": \"(540.0, 1200.0)\", \"Home\": \"(540.0, 1232.5)\", \"Phone\": \"(162.5, 1970.5)\", \"Messages\": \"(414.5, 1970.5)\", \"Chrome\": \"(666.5, 1970.5)\", \"Settings\": \"(918.0, 1970.5)\", \"Search\": \"(539.5, 2207.5)\", \"2:43:21\": \"(221.0, 323.5)\", \"Gmail\": \"(414.0, 1615.0)\", \"Photos\": \"(666.0, 1615.0)\", \"YouTube\": \"(918.0, 1615.0)\", \"Google app\": \"(149.0, 2207.0)\", \"Voice search\": \"(804.0, 2207.5)\", \"Google Lens\": \"(930.0, 2207.5)\", \"15:34\": \"(99.0, 64.5)\", \"SMS Messenger notification: \": \"(177.0, 64.5)\", \"Android System notification: Data warning\": \"(235.0, 64.5)\", \"Clock notification: \": \"(293.0, 64.5)\", \"Phone signal full.\": \"(810.5, 64.0)\", \"Battery 100 percent.\": \"(945.5, 64.5)\", \"No internet\": \"(791.0, 64.0)\"}\n\nPlease generate the low-level thought and action for the next step."}, {"from": "gpt", "value": "Low-level thought: To set a task due date in the Tasks app, the first step is to open the Tasks app.\naction: {\"action_type\":\"open_app\", \"app_name\":\"Tasks\"}"}]}
也就是分为轨迹名称“id”与这是这条轨迹的第几步，本步的图像image，对话内容（prompt与gpt一问一答）的形式
ui部分，每个ui对应的是它的中心点的坐标，并且要规则化(0-1000)。只需要记录有文本描述的ui坐标,也就是有“content_description”的ui
prompt包括任务目标，动作历史，本次的ui list，
gpt的回复分成low level thought和action两个部分
"""

import os
import json
import re

def get_subfolders_sorted(folder_path):
    """
    获取指定文件夹内的所有子文件夹名字，并按字母顺序排序。
    排除以 '.' 开头的隐藏文件夹。
    
    参数:
        folder_path (str): 指定的文件夹路径。
    
    返回:
        list: 子文件夹名字列表，按字母顺序排序。
    """
    # 检查输入路径是否存在
    if not os.path.exists(folder_path):
        print("指定的文件夹路径不存在")
        return []
    
    # 获取指定文件夹内的所有子项
    all_items = os.listdir(folder_path)
    
    # 过滤出子文件夹，并排除以 '.' 开头的隐藏文件夹
    subfolder_names = [item for item in all_items if os.path.isdir(os.path.join(folder_path, item)) and not item.startswith('.')]
    
    # 按字母顺序排序
    subfolder_names.sort()
    
    return subfolder_names

def append_to_jsonl(file_path, item):
    """
    将一个字典追加到 JSONL 文件中。
    
    参数:
        file_path (str): JSONL 文件的路径。
        item (dict): 要写入的字典，表示一个 JSON 对象。
    """
    with open(file_path, 'a', encoding='utf-8') as file:  # 使用追加模式 'a'
        json.dump(item, file, ensure_ascii=False)
        file.write('\n')  # 每个 JSON 对象占一行

def extract_content_description(data):
    """
    检查 ui_description 中是否包含 'content_description'，并提取其对应的值。假如没有的话，也会检查有没有 'text'。
    
    参数:
        data (dict): 包含 ui_description 的字典。
    
    返回:
        str: 如果存在 'content_description' 或 'text'，返回其对应的值；否则返回 None。
    """
    ui_description = data.get("ui_description", "")
    
    # 使用正则表达式提取 'content_description' 或 'text' 的值
    content_description_match = re.search(r'"content_description":\s*"([^"]*)"', ui_description)
    if content_description_match:
        return content_description_match.group(1)
    
    text_match = re.search(r'"text":\s*"([^"]*)"', ui_description)
    if text_match:
        return text_match.group(1)
    
    return None

def extract_content_description_old(data):
    """
    检查 ui_description 中是否包含 'content_description'，并提取其对应的值。假如没有的话，也会检查有没有'text'
    
    参数:
        data (dict): 包含 ui_description 的字典。
    
    返回:
        str: 如果存在 'content_description'，返回其对应的值；否则返回 None。
    """
    ui_description = data.get("ui_description", "")
    
    # 使用正则表达式提取 JSON 部分
    match = re.search(r'\{.*\}', ui_description)
    if not match:
        print("ui_description 中没有找到有效的 JSON 数据")
        return None
    
    json_part = match.group(0)
    
    # 打印提取的 JSON 部分，确保提取的内容是正确的
    #print(f"提取的 JSON 部分: {json_part}")
    
    # 替换双引号，确保符合 JSON 格式
    json_part = json_part.replace('"', '\\"')
    
    # 尝试解析 JSON 数据
    try:
        description_dict = json.loads(json_part)
    except json.JSONDecodeError as e:
        print(f"JSON 解析错误: {e}")
        print(f"本次解析的 ui: {json_part}")
        return None
    
    # 检查是否包含 'content_description'
    if "content_description" in description_dict:
        return description_dict["content_description"]
    elif "text" in description_dict:
        return description_dict["text"]
    else:
        #print("'content_description' 不存在于 ui_description 中")
        return None
    
def get_a11y_tree_str(step_data:dict):
    """
    获取step_data，返回该步对应的ui list。只要有content_description的ui并且中心点的坐标要规则化(0-1000)
    """
    ui_list = step_data["before_ui_elements_list"]
    a11y_tree_dic = {}
    for ui_dic in ui_list:
        content_description = extract_content_description(ui_dic)
        if content_description is None:
            # ui没有content_description字段，跳过
            continue
        # 如果有的话，该ui就要记录.现在开始整理坐标
        ui_bbox = ui_dic["ui_bbox"]
        ui_center_x = (ui_bbox[0]+ui_bbox[2])/2
        ui_center_y = (ui_bbox[1]+ui_bbox[3])/2
        # 规则化坐标.保留一位小数
        ui_center_x = round((ui_center_x/1080)*1000,1)
        ui_center_y = round((ui_center_y/2400)*1000,1)
        # 将元组转换为字符串格式
        ui_center_group_str = f"({ui_center_x}, {ui_center_y})"
        a11y_tree_dic[content_description] = ui_center_group_str

    # 将字典转换为 JSON 格式的字符串
    a11y_tree_str = json.dumps(a11y_tree_dic)
    return a11y_tree_str

folder_path = "/data7/Users/lyx/code/trajectery_folder_for_tdsi"  
jsonl_path = "aw_training_data.jsonl"
subfolder_names = get_subfolders_sorted(folder_path)

for app_name in subfolder_names:
    subfolder_path = app_name
    trajectry_names = get_subfolders_sorted(subfolder_path)
    for trajectry_name in trajectry_names:
        # 开始处理单个轨迹
        trajectry_path = os.path.join(subfolder_path, trajectry_name)
        history_json_path = os.path.join(trajectry_path, "history.json")
        with open(history_json_path, 'r', encoding='utf-8') as file:
            history = json.load(file)
        task_goal_json_path = os.path.join(trajectry_path, "task_goal.json")
        with open(task_goal_json_path, 'r', encoding='utf-8') as file:
            task_goal_dic = json.load(file)
        task_goal = task_goal_dic["task_goal"]
        for i, step_data in enumerate(history):
            # 开始处理该轨迹中的每一步
            step_data_json = {}
            step_data_json["id"] = trajectry_name+"_step_"+str(i+1)
            step_data_json["image"] = os.path.join(trajectry_path, str(i)+".png")

            # 确定谈话内容
            step_data_json["conversations"] = []
            # human端谈话内容
            human_talk = {"from": "human",}
            human_talk_value = "<image>\nYou are a GUI task expert,I will provide you with a high-level instruction, an action history, a screenshot with its corresponding accessibility tree.\n\nHigh-level instruction: "
            human_talk_value += task_goal
            human_talk_value += "\n\n"
            # 获取历史动作
            human_talk_value += "Action history: "
            for hisrory_i in range(i):
                human_talk_value += "step "+str(hisrory_i+1)+","
                human_talk_value += history[hisrory_i]["action_reason"]+" action: "+history[hisrory_i]["action_output_json"]
            human_talk_value += "\n\n"
            # 获取Accessibility tree
            human_talk_value += "Accessibility tree: "
            a11y_tree_str = get_a11y_tree_str(step_data)
            human_talk_value += a11y_tree_str
            human_talk_value += "\n\nPlease generate the low-level thought and action for the next step."
            human_talk["value"] = human_talk_value
            step_data_json["conversations"].append(human_talk)

            # gpt端谈话内容
            gpt_talk = {"from": "gpt",}
            # 获取low_level_thought
            low_level_thought = step_data["action_reason"]
            # 获取action。转化为坐标格式！
            raw_action_str = step_data["action_output_json"]
            raw_action_dic = json.loads(raw_action_str)
            if "index" in raw_action_dic:
                # 把index转化为坐标
                index = raw_action_dic["index"]
                try:
                    target_ui = step_data["before_ui_elements_list"][index]
                except (KeyError, IndexError) as e:
                    print(f"错误: {e}")
                    print("由于数据错误，只能抛弃这一步的数据")
                    continue
                target_ui_bbox = target_ui["ui_bbox"]
                target_ui_bbox_center_x = round((((target_ui_bbox[0]+target_ui_bbox[2])/2)/1080)*1000,1)
                target_ui_bbox_center_y = round((((target_ui_bbox[1]+target_ui_bbox[3])/2)/2400)*1000,1)
                # 创建符合格式的动作
                new_action_dic = raw_action_dic.copy()  # 创建原始字典的副本
                del new_action_dic["index"]  # 删除 "index" 键
                new_action_dic["x"] = target_ui_bbox_center_x  # 添加 "x" 键
                new_action_dic["y"] = target_ui_bbox_center_y  # 添加 "y" 键
                # 将字典转换为 JSON 格式的字符串
                new_action_dic_str = json.dumps(new_action_dic, ensure_ascii=False)
                # 修改history列表中动作的格式
                step_data["action_output_json"] = new_action_dic_str
            else:
                # 没有index，那就可以照抄了
                new_action_dic_str = raw_action_str

            gpt_talk_value = "Low-level thought: "+low_level_thought+"\n"
            gpt_talk_value += "action: "+new_action_dic_str
            gpt_talk["value"] = gpt_talk_value
            step_data_json["conversations"].append(gpt_talk)

            # 保存本步骤进入jsonl文件
            append_to_jsonl(jsonl_path, step_data_json)
        #break
    #break

