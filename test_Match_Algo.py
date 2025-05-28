import unittest
from Match_Algo import match_student, match_universities, match_international_schools

class TestMatchingAlgorithm(unittest.TestCase):
    
    def test_top_public_university_match(self):
        """Test matching for top public universities (NUS, NTU)"""
        result = match_student(
            application_choice="大学",
            academic_percentage=85,
            gaokao_score=650,
            ielts_score=7.0,
            toefl_score=None,
            det_score=None,
            language_pass=True,
            has_high_school_cert=True
        )
        self.assertEqual(result.get("matched_universities"), ["新加坡国立大学", "新加坡南洋理工大学"])
    
    def test_other_public_university_match(self):
        """Test matching for other public universities (SMU, SUTD)"""
        result = match_student(
            application_choice="大学",
            academic_percentage=78,
            gaokao_score=550,
            ielts_score=6.5,
            toefl_score=None,
            det_score=None,
            language_pass=True,
            has_high_school_cert=True
        )
        self.assertEqual(result.get("matched_universities"), ["新加坡管理大学", "新加坡科技设计大学"])
    
    def test_private_university_tier3_match(self):
        """Test matching for private university tier 3"""
        result = match_student(
            application_choice="大学",
            academic_percentage=72,
            gaokao_score=470,
            ielts_score=5.0,
            toefl_score=None,
            det_score=None,
            language_pass=False,
            has_high_school_cert=True
        )
        self.assertEqual(result.get("matched_universities"), ["英国伯明翰大学", "澳大利亚皇家墨尔本理工大学", "爱尔兰都柏林大学"])
        self.assertEqual(result.get("path_to_university"), "进入语言班随后升入国际大一")
    
    def test_private_university_tier4_match(self):
        """Test matching for private university tier 4"""
        result = match_student(
            application_choice="大学",
            academic_percentage=67,
            gaokao_score=430,
            ielts_score=6.5,
            toefl_score=None,
            det_score=None,
            language_pass=True,
            has_high_school_cert=True
        )
        self.assertEqual(result.get("matched_universities"), [
            "澳大利亚伍伦贡大学", "澳洲纽卡斯尔大学", "澳大利亚科廷大学", 
            "新西兰梅西大学", "乐卓博大学"
        ])
        self.assertEqual(result.get("path_to_university"), "进入国际大一")
    
    def test_no_university_match(self):
        """Test case where no universities are matched"""
        result = match_student(
            application_choice="大学",
            academic_percentage=45,
            gaokao_score=300,
            ielts_score=5.0,
            toefl_score=None,
            det_score=None,
            language_pass=False,
            has_high_school_cert=False
        )
        self.assertEqual(result.get("matched_universities"), [])
    
    def test_international_school_high_budget(self):
        """Test matching for international schools with high budget"""
        result = match_student(
            application_choice="国际学校",
            academic_percentage=80,
            has_international_school_experience=True,
            budget_per_year=120000
        )
        self.assertEqual(result.get("matched_international_schools"), 
                         ["UWC", "东陵信托国际学校", "美国国际学校", "德威国际学校", "北伦敦伦敦国际学校"])
    
    def test_international_school_medium_budget(self):
        """Test matching for international schools with medium budget"""
        result = match_student(
            application_choice="国际学校",
            academic_percentage=65,
            has_international_school_experience=False,
            budget_per_year=70000
        )
        self.assertEqual(result.get("matched_international_schools"), 
                         ["斯坦福美国国际学校", "加拿大国际学校", "NPS国际学校", 
                          "澳洲国际学校", "布莱顿国际学校", "多佛国际学校"])
    
    def test_toefl_det_matching(self):
        """Test matching based on TOEFL and DET scores"""
        result = match_student(
            application_choice="大学",
            academic_percentage=82,
            gaokao_score=None,
            ielts_score=None,
            toefl_score=90,
            det_score=110,
            language_pass=True,
            has_high_school_cert=True
        )
        self.assertEqual(result.get("matched_universities"), ["新加坡国立大学", "新加坡南洋理工大学"])

if __name__ == '__main__':
    unittest.main()
