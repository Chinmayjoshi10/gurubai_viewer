import pytest
import banidb

def test_banidb_ang():
    try:
        # Test loading first ang
        ang_data = banidb.angs(1)
        print(f"Ang data: {ang_data}")  # Debug print
        
        # Verify required keys are present
        assert 'page' in ang_data, "Missing 'page' key in ang data"
        assert isinstance(ang_data['page'], list), "Page data should be a list"
        
        # Verify verse structure
        if ang_data['page']:
            verse = ang_data['page'][0]
            assert 'verse' in verse, "Missing 'verse' key in verse data"
            assert 'shabad_id' in verse, "Missing 'shabad_id' key in verse data"
            
            # Test getting shabad details
            shabad_data = banidb.shabad(verse['shabad_id'])
            print(f"Shabad data: {shabad_data}")  # Debug print
            
            assert 'verses' in shabad_data, "Missing 'verses' key in shabad data"
            assert isinstance(shabad_data['verses'], list), "Verses should be a list"
            
            if shabad_data['verses']:
                assert 'steek' in shabad_data['verses'][0], "Missing 'steek' key in verse data"
                assert 'en' in shabad_data['verses'][0]['steek'], "Missing 'en' key in steek data"
                assert 'bdb' in shabad_data['verses'][0]['steek']['en'], "Missing 'bdb' key in English translation"
    except Exception as e:
        print(f"Error in test: {str(e)}")
        raise

def test_ang_data_structure():
    """Test that banidb.ang returns the expected data structure"""
    ang_data = banidb.ang(1)
    
    assert "text" in ang_data, "Missing 'text' key in ang data"
    assert "transliteration" in ang_data, "Missing 'transliteration' key in ang data"
    assert "translation" in ang_data, "Missing 'translation' key in ang data"
    
    assert isinstance(ang_data["text"], str), "Text should be a string"
    assert isinstance(ang_data["transliteration"], str), "Transliteration should be a string"
    assert isinstance(ang_data["translation"], str), "Translation should be a string"

def test_ang_content():
    """Test that ang data contains actual content"""
    ang_data = banidb.ang(1)
    
    assert len(ang_data["text"]) > 0, "Text should not be empty"
    assert len(ang_data["transliteration"]) > 0, "Transliteration should not be empty"
    assert len(ang_data["translation"]) > 0, "Translation should not be empty" 