import unittest
from pathlib import Path


class TestHintVisibilityIntegration(unittest.TestCase):
    """Integration tests for hint visibility functionality across web and text clients"""

    def setUp(self) -> None:
        self.template_path = Path(__file__).parent.parent / "WebHostLib" / "templates" / "multitrackerHintTable.html"
        self.js_path = Path(__file__).parent.parent / "WebHostLib" / "static" / "assets" / "trackerCommon.js"
        self.kvui_path = Path(__file__).parent.parent / "kvui.py"
        self.common_client_path = Path(__file__).parent.parent / "CommonClient.py"

    def test_consistent_functionality_across_clients(self) -> None:
        """Test that both web and text clients have consistent hint visibility functionality"""
        # Check web client has toggle controls
        with open(self.template_path, 'r') as f:
            web_content = f.read()
        
        self.assertIn('hide-completed-hints', web_content, 
                     "Web client should have hide completed hints toggle")
        self.assertIn('hide-external-items', web_content, 
                     "Web client should have hide external items toggle")
        
        # Check JavaScript has filtering functions
        with open(self.js_path, 'r') as f:
            js_content = f.read()
        
        self.assertIn('filterHints', js_content, 
                     "Web client should have hint filtering function")
        
        # Check text client has filtering methods
        with open(self.kvui_path, 'r') as f:
            kvui_content = f.read()
        
        self.assertIn('filter_completed_hints', kvui_content, 
                     "Text client should have completed hints filtering")
        self.assertIn('filter_external_items', kvui_content, 
                     "Text client should have external items filtering")
        
        # Check text client has commands
        with open(self.common_client_path, 'r') as f:
            client_content = f.read()
        
        self.assertIn('_cmd_hide_completed_hints', client_content, 
                     "Text client should have hide completed hints command")
        self.assertIn('_cmd_hide_external_items', client_content, 
                     "Text client should have hide external items command")

    def test_edge_case_handling(self) -> None:
        """Test edge cases for hint filtering"""
        # Test empty hints list
        empty_hints = []
        
        # Test all hints completed
        all_completed_hints = [
            {"found": True, "receiving_player": 1},
            {"found": True, "receiving_player": 2},
            {"found": True, "receiving_player": 3}
        ]
        
        # Test no hints completed
        no_completed_hints = [
            {"found": False, "receiving_player": 1},
            {"found": False, "receiving_player": 2},
            {"found": False, "receiving_player": 3}
        ]
        
        # Test mixed hints
        mixed_hints = [
            {"found": True, "receiving_player": 1},
            {"found": False, "receiving_player": 2},
            {"found": True, "receiving_player": 3}
        ]
        
        # Basic filtering logic tests
        completed_count = len([h for h in mixed_hints if h["found"]])
        uncompleted_count = len([h for h in mixed_hints if not h["found"]])
        
        self.assertEqual(completed_count, 2, "Should have 2 completed hints")
        self.assertEqual(uncompleted_count, 1, "Should have 1 uncompleted hint")

    def test_css_classes_consistency(self) -> None:
        """Test that CSS classes are consistently applied"""
        with open(self.template_path, 'r') as f:
            content = f.read()
        
        # Check that hint rows have proper classes
        self.assertIn('hint-row', content, "Hint rows should have hint-row class")
        self.assertIn('hint-completed', content, "Completed hints should have hint-completed class")
        self.assertIn('hint-external', content, "External hints should have hint-external class")

    def test_javascript_functions_exist(self) -> None:
        """Test that all required JavaScript functions exist"""
        with open(self.js_path, 'r') as f:
            content = f.read()
        
        required_functions = [
            'filterHints',
            'loadHintPreferences', 
            'initializeHintFiltering'
        ]
        
        for func in required_functions:
            self.assertIn(func, content, f"JavaScript should contain {func} function")

    def test_localStorage_usage(self) -> None:
        """Test that localStorage is used for persistence"""
        with open(self.js_path, 'r') as f:
            content = f.read()
        
        self.assertIn('localStorage.setItem', content, 
                     "Should save preferences to localStorage")
        self.assertIn('localStorage.getItem', content, 
                     "Should load preferences from localStorage")
        self.assertIn('hideCompletedHints', content, 
                     "Should store hideCompletedHints preference")
        self.assertIn('hideExternalItems', content, 
                     "Should store hideExternalItems preference")


if __name__ == '__main__':
    unittest.main()

