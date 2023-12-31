import streamlit as st
import json
import openai
from datetime import datetime
from openai import OpenAI

def run():
    # 设置 API 端点和 OpenAI API 密钥
    client = OpenAI(api_key=st.secrets["1"], base_url=st.secrets["2"])

    response = False
    if 'Outline' not in st.session_state:
        st.session_state['Outline'] = ""
    if 'OutlineObj' not in st.session_state:
        st.session_state['OutlineObj'] = {}
    if 'sectionsList' not in st.session_state:
        st.session_state['sectionsList'] = []
    if 'finished' not in st.session_state:
        st.session_state['finished'] = False

    # 设置标题
    st.title('管理硕士作业写作助手')
    st.subheader('此助手可以根据你的撰写范围方向及写作纲要作业要求，生成5000字以内的作业（包含题目·正文·参考文献）')
    st.subheader('请你根据你的作业需求填写一下作业要求，填写的比较详细生成内容越符合作业要求')


    # 为用户提供输入框
    st.markdown('##### 1.请输入你的作业题目，或者输入你的作业写作方向，我帮你你生成作业题目（此处描绘的要清楚·必须填写）📜')
    title = st.text_input('作业题目')
    st.markdown('##### 作业语言要求 中文 英文 （必填）')
    language = st.selectbox('作业语言',["中文","English"])
    st.markdown('##### 作业字数要求（必填）')
    counts = st.text_input('作业字数')
    st.markdown('##### 作业章节要求，第一章节xxxx，第二章节xxxx等 （若作业没有相关要求可以不添），我帮你生成章节')
    angle_and_conclusion = st.text_area('章节介绍（可选）')
    st.markdown('##### 作业其他要求，在这里输入（如果没有可以不添）')
    additional_info = st.text_area('其他要求（可选）')

    # 提供一个按钮，点击后生成大纲
    if st.button('生成文章'):
        if not title or not language or not counts:
            # 如果用户名或密码为空，则显示警告信息
            st.warning("请填写必须填写的信息")
        else:
            messages = []
            GPT_response = st.empty()
            prompt = f"""
            ## 任务
            根据以下的信息进行文章大纲的创作，为该文章取一个醒目的名称，并为每个章节生成一些概括性内容
            1. **主题和焦点**：
                - 文章的标题和范围：{title}
                - 作业的要求 {angle_and_conclusion}
                - 是否有一些附加信息为我提供最新的内容? {additional_info}
            2. **写作任务**：
                - 文章的类型？这是一篇论文作业
                - 你希望让读者通过文章获得什么样的体验或信息？希望能够论证自己的观点
                - 输出的语言为 {language}
            3. **文章风格**：
                - 你希望文章的语调或风格是怎样的？学术
            4. **格式和结构**：
                - 引言 // 必须要有，对全文做一个总结性的说明
                - 3-4个章节 // 根据文章的字数{counts}，来构建章节，3000以上为3章，4000字以上为4章
                - 结论 // 必须要有，对全文的结论做一个说明
                - 参考文献 // **参考文献必须真实有效，并有权威的来源**，比如google scholars或者百度文献
            """
            # test = f"鲁迅和周树人的关系"
            with st.spinner("正在生成大纲，请稍候..."):
                chat_completion = client.chat.completions.create(
                    model="gpt-4-1106-preview",
                    messages=[
                        {"role": "system", "content": "你是一名文章写手,以markdown格式输出"},
                        {"role": "user", "content": prompt},
                        ],
                    stream=True,
                )

                for token in chat_completion:
                    content = token.choices[0].delta.content # new API result
                    if content != None:
                        messages.append(content)
                        full_reply_content = ''.join([m for m in messages])
                        GPT_response.markdown(f"🤖: {full_reply_content}")

                st.session_state['Outline'] = full_reply_content
                st.rerun()

        if st.session_state['Outline']:
            #st.write(st.session_state['Outline'])
            if st.session_state['finished']:
                st.write(st.session_state['Outline'])
                st.write(st.session_state['OutlineObj'])
                st.write(st.session_state['sectionsList'])

                chat_text = ""
                chat_text += f"# {st.session_state['OutlineObj']['title']} \n"
                sectionsList = st.session_state['sectionsList']
                i=0

                while i < len(sectionsList):
                    chat_text += f"## {st.session_state['OutlineObj']['sections'][i]} \n"
                    chat_text += f"{sectionsList[i]}\n"
                    i = i+1
                
                references = st.session_state['OutlineObj']['references']
                j=0

                chat_text += f"## 参考文献\n"
                while j < len(references):
                    chat_text += f"{j+1}. {st.session_state['OutlineObj']['references'][j]} \n"
                    j = j+1
                        
                # 添加下载按钮
                timestamp = datetime.now()
                file_name = f"Article_records_{timestamp}.txt"
                st.download_button(
                    label="下载文章",
                    data=chat_text,
                    file_name=file_name,
                    mime="text/plain"
                    )
            
            else:
                if st.session_state['OutlineObj']:
                    st.write(st.session_state['OutlineObj'])
                    st.write("开始按照章节目录来进行内容的生成")
                    title = st.session_state['OutlineObj']["title"]
                    sections = st.session_state['OutlineObj']["sections"]
                    for section in sections:
                        msg = f"扩写标题：{title}下的章节:{section},请稍后..."
                        with st.spinner(msg):
                            messages = []
                            GPT_response = st.empty()

                            prompt = f"""
                            # MBA作业助手-扩写
                            ## 任务
                            1. 基于<大纲>, 结合标题 {title} ,**仅对 {section} 部分进行扩写**，需要至少1000汉字的内容
                            1.1 **注意不需要输出章节的标题！！**
                            1.2 **注意不需要直接输出参考文献！！但需要在原文中利用角标进行参考文献的标注**
                            2. 结合<注意事项>进行内容的输出
                            ## 大纲
                            {st.session_state['Outline']}
                            ## 注意事项
                            1. **目标受众**：
                                - 这是一篇论文作业
                                - 希望能够论证自己的观点
                            2. **文章风格**：
                                - 学术 //注意，不要以‘我们’的口吻进行输出，要突出你的贡献
                            3. **图表或视觉元素**：
                                - 在需要进行插入视觉元素的地方进行标注
                            4. **参考文献**：
                                - **不需要输出参考文献，但需要在原文中利用角标进行参考文献的标注**
                            """

                            chat_completion = client.chat.completions.create(
                                model="gpt-4-1106-preview",
                                messages=[
                                    {"role": "system", "content": ""},
                                    {"role": "user", "content": prompt}
                                ],
                                stream=True,
                            )

                            if isinstance(chat_completion, dict):
                                # not stream
                                st.write(chat_completion.choices[0].message.content)
                            else:
                                # stream
                                for token in chat_completion:
                                    content = token.choices[0].delta.content # new API result
                                    if content != None:
                                        messages.append(content)
                                        full_reply_content = ''.join([m for m in messages])
                                        GPT_response.markdown(f"🤖: {full_reply_content}")

                                st.session_state['sectionsList'].append(full_reply_content)                       
                    st.session_state['finished'] = True
                    st.rerun()
                
                else:
                    with st.spinner("正在分析大纲内容，请稍候..."):
                        messages = []
                        GPT_response = st.empty()

                        prompt = f"""
                            # OutlineToJson
                            ## Task
                            * READ THE <outline> and OUTPUT A JSON STRING ONLY!!!.without any markdown symbol
                            * the Json String is DEFINED by <JSON Format>
                            * MAKE SURE your output can be pharsed by json.load() directly!
                            ### JSON Format
                            {{
                                "title": "文章标题",
                                "sections": [], //只需要返回章节（包含引言和结论）的title即可，不需要返回章节内容！！！
                                "references":[], //将参考文献保存为一个列表
                            }}
                            ### outline
                            {st.session_state['Outline']}
                        """

                        chat_completion = client.chat.completions.create(
                            model="gpt-4-1106-preview",
                            response_format={"type": "json_object"},
                            messages=[
                                {"role": "system", "content": ""},
                                {"role": "user", "content": prompt}
                                ],
                            stream=True,
                        )

                        if isinstance(chat_completion, dict):
                            # not stream
                            st.write(chat_completion.choices[0].message.content)
                        else:
                            # stream
                            for token in chat_completion:
                                content = token.choices[0].delta.content # new API result
                                if content != None:
                                    messages.append(content)
                                    full_reply_content = ''.join([m for m in messages])
                                    GPT_response.markdown(f"🤖: {full_reply_content}")
                            # jsonstring=full_reply_content.replace('```json','')
                            st.write(full_reply_content)
                            st.session_state['OutlineObj'] = json.loads(full_reply_content)
                            st.rerun()