import pandas as pd
from src.SQL_query import sql_operation
from src.find_bank_name import bank_name
from src.find_topic_name import topic_name


def get_bank_name(text):
    name_list = bank_checker.check_bank_name(text)
    return name_list


def get_topic_name(text):
    name_list = topic_checker.check_topic_name(text)
    return name_list


def split_by_paragraph(text):
    paragraphs = text.split('\n')
    paragraphs = [paragraph.strip() for paragraph in paragraphs if paragraph.strip()]
    return paragraphs


def segmenting():
    # Check duplicate
    df_sac_thai = sql.get_info('SAC_THAI')
    already_segmented = list(set(df_sac_thai['id_ban_tin']))

    # Preprocess data BAN_TIN
    df = sql.get_info('BAN_TIN')
    df = df.loc[~df['id_ban_tin'].isin(already_segmented)]
    df.loc[:, 'bank_name'] = df['text'].apply(get_bank_name)
    df.loc[:, 'topic_name'] = df['text'].apply(get_topic_name)

    # Filter out rows with no bank_name or topic_name
    df_process = df.loc[(df['bank_name'] != False) & (df['topic_name'] != False), ['id_ban_tin', 'text', 'bank_name', 'topic_name']]
    if not df_process.empty:
        df_process["Ngay"] = df["Ngay"]
    df_process.reset_index(inplace=True, drop=True)
    df_process['paragraphs'] = df_process['text'].apply(split_by_paragraph)

    # For data without bank but catch topic
    df_only_topic = df.loc[(df['bank_name'] == False) & (df['topic_name'] != False), ['id_ban_tin', 'text', 'bank_name', 'topic_name']]
    if not df_only_topic.empty:
        df_only_topic["Ngay"] = df["Ngay"]
    df_only_topic.reset_index(inplace=True, drop=True)
    df_only_topic['paragraphs'] = df_only_topic['text'].apply(split_by_paragraph)
    
    added = 0

    for index, row in df_process.iterrows():
        bank_list = row['bank_name'].split(',')
        topic_list = row['topic_name'].split(',')
        paragraphs = row['paragraphs']

        for bank in bank_list:
            for topic in topic_list:
                segment = ""
                for paragraph in paragraphs:
                    if bank_checker.check_specific_bank(bank, paragraph) and topic_checker.check_specific_topic(topic, paragraph):
                        segment += paragraph + "\n"

                if segment:
                    added += 1
                    sql.insert_to_db('SAC_THAI', "text_paragraph,chu_de,ngan_hang,id_ban_tin,Ngay", (f"N'{segment}'", f"N'{topic}'", f"N'{bank}'", f"'{row['id_ban_tin']}'", f"N'{row['Ngay']}'"))
                else:
                    print(f"Cannot find: {bank} and topic: {topic} in id_ban_tin: {row['id_ban_tin']}")

    for index, row in df_only_topic.iterrows():
        topic_list = row['topic_name'].split(',')
        paragraphs = row['paragraphs']

        for topic in topic_list:
            segment = ""
            for paragraph in paragraphs:
                if topic_checker.check_specific_topic(topic, paragraph):
                    segment += paragraph + "\n"

            if segment:
                added += 1
                sql.insert_to_db('SAC_THAI', "text_paragraph,chu_de,id_ban_tin,Ngay", (f"N'{segment}'", f"N'{topic}'", f"'{row['id_ban_tin']}'", f"N'{row['Ngay']}'"))
            else:
                print(f"Cannot find: topic {topic} in id_ban_tin: {row['id_ban_tin']}")

    return 'Completed!'


sql = sql_operation()
bank_checker = bank_name()
topic_checker = topic_name()

print(segmenting())
