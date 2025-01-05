import random
import pandas as pd


def create_shuffled_data(
    in_data_tsv: str,
    out_data_tsv: str,
    out_meta_tsv: str,
    n_questions_per_user: int=3,
    n_redundancy: int=2,
    seed: int=0,
    insert_check_randomly: bool=True,
):
    """設問データをランダムシャッフルしてTSVファイルに出力します。

    Parameters:
        in_data_tsv: 元の設問データTSVパス。  
            2列目が0なら通常設問、1ならチェック設問、それ以外なら固定設問と見做します。
            固定設問はその順に各ユーザに問います (なくても構いません)。
            チェック設問は各ユーザに問います (なくても構いません)。
            通常設問は `n_questions_per_user` 問ずつ各ユーザに問います。
            **通常設問の行数が `n_questions_per_user` の整数倍でなければなりません。**
        out_data_tsv: シャッフル後の設問データTSVを出力するパス。  
            列名は `in_data_tsv` の列名を維持します。1列目にユニークIDがふられます。
        out_meta_tsv: 突合用メタデータTSVを出力するパス。  
            1列目は `out_data_tsv` と対応するユニークID、
            2列目はユーザID (0から通し番号をふっているだけ)、
            3列目は元の設問データにおけるインデクスを出力します。
        n_questions_per_user: 1ユーザあたりに問う通常設問数 (固定設問とチェック設問は除く)。
        n_redundancy: 冗長数 (1つの通常設問に何ユーザの回答を得るか)。
        seed: 乱数のシード。
        insert_check_randomly: チェック設問位置をランダムにするか。
    """
    random.seed(seed)
    df = pd.read_csv(in_data_tsv, sep='\t', dtype=str, keep_default_na=False)
    df_fixed = df[~df[df.columns[1]].isin(['0', '1'])].copy()
    df_check = df[df[df.columns[1]]=='1']
    df_questions = df[df[df.columns[1]]=='0']
    df.loc[df_fixed.index, df.columns[1]] = '0'  # 入稿データでは 0 にする必要がある。

    if len(df_questions) % n_questions_per_user != 0:
        raise ValueError(
            f'通常設問数{len(df_questions)}が1人あたり設問数{n_questions_per_user}の倍数でない'
        )

    n_user = int((len(df_questions) * n_redundancy) / n_questions_per_user)
    index_org = list(df_questions.index)
    index_shuffled = []
    for i_redundancy in range(n_redundancy):
        index_shuffled += random.sample(index_org, len(index_org))

    ofile_data = open(out_data_tsv, mode='w', encoding='utf8', newline='\n')
    ofile_meta = open(out_meta_tsv, mode='w', encoding='utf8', newline='\n')

    ofile_data.write('\t'.join(df.columns) + '\n')
    ofile_meta.write('qid\ti_user\tindex\n')

    qid = 0
    for i_user in range(n_user):
        i_0 = n_questions_per_user * i_user
        i_1 = i_0 + n_questions_per_user
        index_ = index_shuffled[i_0:i_1]

        if insert_check_randomly:
            for index_check in df_check.index:
                random_index = random.randint(0, len(index_))
                index_.insert(random_index, index_check)
        else:
            index_ = list(df_check.index) + index_
        index_ = list(df_fixed.index) + index_

        for index, row in df.loc[index_, :].iterrows():
            qid += 1
            ofile_data.write(f'{qid:06}\t' + '\t'.join(row[1:]) + '\n')
            ofile_meta.write(f'{qid:06}\t{i_user}\t{index}\n')

    ofile_data.close()
    ofile_meta.close()
