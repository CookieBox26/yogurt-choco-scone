import unittest
import tempfile
import os
import yogurt_choco_scone as ycs
import pandas as pd


class TestYogurtChocoScone(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.out_data_tsv = os.path.join(self.temp_dir.name, 'out_data.tsv')
        self.out_meta_tsv = os.path.join(self.temp_dir.name, 'out_meta.tsv')

    def tearDown(self):
        self.temp_dir.cleanup()

    def create_temp_csv(self, data):
        temp_tsv = os.path.join(self.temp_dir.name, 'data.tsv')
        df = pd.DataFrame(data)
        df.to_csv(temp_tsv, sep='\t', index=False, header=False)
        return temp_tsv

    def test_create_shuffled_data(self):
        data = [
            ['V1', 'V2', 'V3', 'V4', 'V5'],
            ['', '-1', '', 'あなたの性別は？', '男性@女性@その他'],
            ['', '1', 'レモン@バナナ', '黄色い果物は？', 'りんご@レモン@バナナ'],
            ['', '0', '', '好きな果物は？', 'りんご@みかん@バナナ'],
            ['', '0', '', '好きな果物は？', 'ぶどう@レモン@キウイ'],
            ['', '0', '', '好きな果物は？', 'メロン@いちご@ライチ'],
            ['', '0', '', '好きな果物は？', 'パイン@すいか@洋なし'],
            ['', '0', '', '好きな果物は？', 'あんず@あけび@ざくろ'],
            ['', '0', '', '好きな菓子は？', '今川焼@大判焼@回転焼'],
        ]
        temp_tsv = self.create_temp_csv(data)
        ycs.create_shuffled_data(
            temp_tsv, self.out_data_tsv, self.out_meta_tsv,
            n_questions_per_user=3, n_redundancy=2,
            insert_check_randomly=True,
        )

        # 6問を3問ずつ問うので1周問うのに必要人数2人
        # 冗長数2にするために必要人数4人
        # 固定設問とチェック設問を合わせたときの1人あたり設問数5問
        # 期待する出力行数は5問×4人=20行
        df_data = pd.read_csv(self.out_data_tsv, sep='\t')
        df_meta = pd.read_csv(self.out_meta_tsv, sep='\t')
        self.assertEqual(len(df_data), 20)
        self.assertEqual(len(df_meta), 20)
        self.assertTrue(all(df_data.iloc[:, 1].isin([0, 1])))
        self.assertTrue(all(df_data.iloc[0::5, 3] == 'あなたの性別は？'))

    def test_create_shuffled_data_without_fixed_questions(self):
        data = [
            ['V1', 'V2', 'V3', 'V4', 'V5'],
            ['', '1', 'レモン@バナナ', '黄色い果物は？', 'りんご@レモン@バナナ'],
            ['', '0', '', '好きな果物は？', 'りんご@みかん@バナナ'],
            ['', '0', '', '好きな果物は？', 'ぶどう@レモン@キウイ'],
            ['', '0', '', '好きな果物は？', 'メロン@いちご@ライチ'],
            ['', '0', '', '好きな果物は？', 'パイン@すいか@洋なし'],
            ['', '0', '', '好きな果物は？', 'あんず@あけび@ざくろ'],
            ['', '0', '', '好きな菓子は？', '今川焼@大判焼@回転焼'],
        ]
        temp_tsv = self.create_temp_csv(data)
        out_data_tsv = os.path.join(self.temp_dir.name, 'out_data.tsv')
        out_meta_tsv = os.path.join(self.temp_dir.name, 'out_meta.tsv')
        ycs.create_shuffled_data(
            temp_tsv, self.out_data_tsv, self.out_meta_tsv,
            n_questions_per_user=3, n_redundancy=2,
            insert_check_randomly=True,
        )
        df_data = pd.read_csv(self.out_data_tsv, sep='\t')
        df_meta = pd.read_csv(self.out_meta_tsv, sep='\t')
        self.assertEqual(len(df_data), 16)
        self.assertEqual(len(df_meta), 16)
        self.assertTrue(all(df_data.iloc[:, 1].isin([0, 1])))
