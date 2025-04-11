import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QComboBox, QPushButton, QScrollArea, QFileDialog, QGridLayout)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QColor, QPalette
import random
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

# Λεξικά μεταφράσεων (updated titles)
translations = {
    "el": {
        "title": "Διαιτολόγιο",  # Changed from "Διαιτολόγιο 2025"
        "goal_label": "Στόχος",
        "weight_label": "Βάρος (kg)",
        "height_label": "Ύψος (cm)",
        "age_label": "Ηλικία",
        "gender_label": "Φύλο",
        "activity_label": "Ενέργεια",
        "calculate_btn": "Υπολογισμός",
        "save_btn": "Αποθήκευση",
        "info_default": "Εισάγετε τα στοιχεία σας",
        "goals": ["Απώλεια", "Συντήρηση", "Μυϊκή Αύξηση"],
        "genders": ["Άνδρας", "Γυναίκα", "Άλλο"],
        "activities": ["Χαλαρή", "Ελαφριά", "Μέτρια", "Έντονη", "Εξτρίμ"],
        "days": ["Δευτέρα", "Τρίτη", "Τετάρτη", "Πέμπτη", "Παρασκευή", "Σάββατο", "Κυριακή"],
        "meals": {"πρωινό": "Πρωινό", "σνακ1": "Σνακ (Πρωί)", "μεσημεριανό": "Μεσημεριανό", "σνακ2": "Σνακ (Απόγευμα)", "βραδινό": "Βραδινό"},
        "plan_title": "Εβδομαδιαίο Διατροφικό Πλάνο",
        "goal_info": "Στόχος",
        "calories_info": "Θερμίδες",
        "protein_info": "Πρωτεΐνη",
        "carbs_info": "Υδατάνθρακες",
        "fat_info": "Λίπος",
        "created_info": "Δημιουργήθηκε",
        "error_fields": "Παρακαλώ συμπληρώστε όλα τα πεδία!",
        "error_positive": "Τα στοιχεία πρέπει να είναι θετικοί αριθμοί!",
        "error_numbers": "Σφάλμα: Εισάγετε έγκυρους αριθμούς! ({})",
        "error_general": "Σφάλμα: {}",
        "saved": "Αποθηκεύτηκε!",
        "error_save": "Σφάλμα αποθήκευσης: {}"
    },
    "en": {
        "title": "Diet Plan",  # Changed from "Diet Plan 2025"
        "goal_label": "Goal",
        "weight_label": "Weight (kg)",
        "height_label": "Height (cm)",
        "age_label": "Age",
        "gender_label": "Gender",
        "activity_label": "Activity",
        "calculate_btn": "Calculate",
        "save_btn": "Save",
        "info_default": "Enter your details",
        "goals": ["Loss", "Maintenance", "Muscle Gain"],
        "genders": ["Male", "Female", "Other"],
        "activities": ["Sedentary", "Light", "Moderate", "Active", "Extreme"],
        "days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
        "meals": {"πρωινό": "Breakfast", "σνακ1": "Snack (Morning)", "μεσημεριανό": "Lunch", "σνακ2": "Snack (Afternoon)", "βραδινό": "Dinner"},
        "plan_title": "Weekly Diet Plan",
        "goal_info": "Goal",
        "calories_info": "Calories",
        "protein_info": "Protein",
        "carbs_info": "Carbs",
        "fat_info": "Fat",
        "created_info": "Created",
        "error_fields": "Please fill all fields!",
        "error_positive": "Details must be positive numbers!",
        "error_numbers": "Error: Enter valid numbers! ({})",
        "error_general": "Error: {}",
        "saved": "Saved!",
        "error_save": "Save error: {}"
    }
}

# Υπολογισμοί
def calculate_bmr(weight, height, age, gender):
    if gender in ["Άνδρας", "Male"]: return 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
    elif gender in ["Γυναίκα", "Female"]: return 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)
    else: return (88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age) + 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)) / 2

def calculate_tdee(bmr, activity_level):
    activity_multipliers = {"Χαλαρή": 1.2, "Ελαφριά": 1.375, "Μέτρια": 1.55, "Έντονη": 1.725, "Εξτρίμ": 1.9,
                           "Sedentary": 1.2, "Light": 1.375, "Moderate": 1.55, "Active": 1.725, "Extreme": 1.9}
    return bmr * activity_multipliers.get(activity_level, 1.55)

def calculate_target_calories(tdee, goal):
    if goal in ["Απώλεια", "Loss"]: return tdee - 500
    elif goal in ["Μυϊκή Αύξηση", "Muscle Gain"]: return tdee + 300
    else: return tdee

def calculate_macros(target_calories, macro_ratio):
    protein_pct, carb_pct, fat_pct = macro_ratio
    return {"πρωτεΐνη": round((target_calories * (protein_pct / 100)) / 4), 
            "υδατάνθρακες": round((target_calories * (carb_pct / 100)) / 4), 
            "λίπος": round((target_calories * (fat_pct / 100)) / 9)}

# Τρόφιμα με θρεπτικά συστατικά ανά 100g και τυπικές μερίδες
food_data = {
    "proteins": {
        "κοτόπουλο στήθος": {"protein": 31, "carbs": 0, "fat": 3.6, "portion": 120, "en": "chicken breast"},
        "σολομός": {"protein": 25, "carbs": 0, "fat": 13, "portion": 100, "en": "salmon"},
        "τόνος (κονσέρβα)": {"protein": 29, "carbs": 0, "fat": 1, "portion": 80, "en": "tuna (canned)"},
        "αυγά": {"protein": 13, "carbs": 1, "fat": 11, "portion": 100, "en": "eggs"},
        "γιαούρτι 2%": {"protein": 10, "carbs": 4, "fat": 2, "portion": 150, "en": "yogurt 2%"},
        "φακές": {"protein": 9, "carbs": 20, "fat": 0.4, "portion": 80, "en": "lentils"},
        "μοσχάρι (άπαχο)": {"protein": 26, "carbs": 0, "fat": 7, "portion": 100, "en": "beef (lean)"},
        "γαλοπούλα": {"protein": 29, "carbs": 0, "fat": 1, "portion": 100, "en": "turkey"},
        "λευκό ψάρι (μπακαλιάρος)": {"protein": 23, "carbs": 0, "fat": 0.7, "portion": 120, "en": "white fish (cod)"},
        "ρεβίθια": {"protein": 9, "carbs": 27, "fat": 3, "portion": 80, "en": "chickpeas"},
        "φακές κόκκινες": {"protein": 8, "carbs": 20, "fat": 0.5, "portion": 80, "en": "red lentils"},
        "τυρί cottage": {"protein": 11, "carbs": 3, "fat": 4, "portion": 100, "en": "cottage cheese"}
    },
    "carbs": {
        "ρύζι καστανό": {"protein": 3, "carbs": 23, "fat": 0.9, "portion": 70, "en": "brown rice"},
        "πατάτες": {"protein": 2, "carbs": 17, "fat": 0.1, "portion": 150, "en": "potatoes"},
        "ψωμί ολικής": {"protein": 9, "carbs": 41, "fat": 3, "portion": 40, "en": "whole wheat bread"},
        "ζυμαρικά ολικής": {"protein": 5, "carbs": 25, "fat": 1, "portion": 80, "en": "whole wheat pasta"},
        "κινόα": {"protein": 14, "carbs": 21, "fat": 6, "portion": 60, "en": "quinoa"},
        "βρώμη": {"protein": 13, "carbs": 66, "fat": 7, "portion": 40, "en": "oats"},
        "γλυκοπατάτες": {"protein": 1.6, "carbs": 20, "fat": 0.1, "portion": 130, "en": "sweet potatoes"},
        "φαγόπυρο": {"protein": 13, "carbs": 72, "fat": 3.4, "portion": 50, "en": "buckwheat"},
        "κους κους": {"protein": 13, "carbs": 77, "fat": 0.6, "portion": 50, "en": "couscous"},
        "ρύζι μπασμάτι": {"protein": 3, "carbs": 28, "fat": 0.4, "portion": 70, "en": "basmati rice"},
        "ψωμί σίκαλης": {"protein": 8, "carbs": 48, "fat": 1.3, "portion": 40, "en": "rye bread"}
    },
    "fats": {
        "ελαιόλαδο": {"protein": 0, "carbs": 0, "fat": 100, "portion": 10, "en": "olive oil"},
        "αβοκάντο": {"protein": 2, "carbs": 9, "fat": 15, "portion": 50, "en": "avocado"},
        "ξηροί καρποί (αμύγδαλα)": {"protein": 21, "carbs": 10, "fat": 50, "portion": 25, "en": "nuts (almonds)"},
        "ταχίνι": {"protein": 17, "carbs": 21, "fat": 54, "portion": 15, "en": "tahini"},
        "φιστίκια": {"protein": 26, "carbs": 16, "fat": 49, "portion": 25, "en": "peanuts"},
        "βούτυρο αμυγδάλου": {"protein": 21, "carbs": 19, "fat": 56, "portion": 15, "en": "almond butter"},
        "σπόροι chia": {"protein": 17, "carbs": 42, "fat": 31, "portion": 20, "en": "chia seeds"},
        "λιναρόσπορος": {"protein": 18, "carbs": 29, "fat": 42, "portion": 15, "en": "flaxseeds"},
        "μέλι": {"protein": 0.3, "carbs": 82, "fat": 0, "portion": 10, "en": "honey"}
    },
    "vegetables": {
        "μπρόκολο": {"protein": 3, "carbs": 7, "fat": 0.4, "portion": 80, "en": "broccoli"},
        "σπανάκι": {"protein": 3, "carbs": 4, "fat": 0.4, "portion": 40, "en": "spinach"},
        "ντομάτα": {"protein": 1, "carbs": 4, "fat": 0.2, "portion": 60, "en": "tomato"},
        "αγγούρι": {"protein": 1, "carbs": 4, "fat": 0.1, "portion": 40, "en": "cucumber"},
        "πιπεριές": {"protein": 1, "carbs": 6, "fat": 0.2, "portion": 50, "en": "bell peppers"},
        "κολοκυθάκια": {"protein": 1, "carbs": 3, "fat": 0.3, "portion": 80, "en": "zucchini"},
        "καρότα": {"protein": 1, "carbs": 10, "fat": 0.2, "portion": 60, "en": "carrots"},
        "κουνουπίδι": {"protein": 2, "carbs": 5, "fat": 0.3, "portion": 80, "en": "cauliflower"},
        "μελιτζάνες": {"protein": 1, "carbs": 6, "fat": 0.2, "portion": 70, "en": "eggplant"}
    },
    "fruits": {
        "μήλο": {"protein": 0.3, "carbs": 14, "fat": 0.2, "portion": 120, "en": "apple"},
        "μπανάνα": {"protein": 1, "carbs": 23, "fat": 0.3, "portion": 100, "en": "banana"},
        "πορτοκάλι": {"protein": 1, "carbs": 12, "fat": 0.2, "portion": 130, "en": "orange"},
        "φράουλες": {"protein": 0.7, "carbs": 8, "fat": 0.3, "portion": 100, "en": "strawberries"},
        "ακτινίδιο": {"protein": 1, "carbs": 15, "fat": 0.5, "portion": 80, "en": "kiwi"},
        "ρόδι": {"protein": 1.7, "carbs": 19, "fat": 1.2, "portion": 100, "en": "pomegranate"},
        "μπλούμπερι": {"protein": 0.7, "carbs": 14, "fat": 0.3, "portion": 80, "en": "blueberries"}
    }
}

# Ρεαλιστικές συνταγές
recipes = {
    "πρωινό": [
        ("Ομελέτα με {0}g αυγά, {1}g σπανάκι και {2}g ντομάτα, με 1 φέτα ({3}g) ψωμί ολικής", ["αυγά", "σπανάκι", "ντομάτα", "ψωμί ολικής"], "Omelette with {0}g eggs, {1}g spinach, {2}g tomato, and 1 slice ({3}g) whole wheat bread"),
        ("Πορριτζ με {0}g βρώμη, {1}g γιαούρτι 2% και {2}g μπανάνα", ["βρώμη", "γιαούρτι 2%", "μπανάνα"], "Porridge with {0}g oats, {1}g 2% yogurt, and {2}g banana"),
        ("Τοστ με {0}g ψωμί ολικής, {1}g αβοκάντο και {2}g αυγό ποσέ", ["ψωμί ολικής", "αβοκάντο", "αυγά"], "Toast with {0}g whole wheat bread, {1}g avocado, and {2}g poached egg"),
        ("Σμούθι με {0}g γιαούρτι 2%, {1}g φράουλες και {2}g σπόρους chia", ["γιαούρτι 2%", "φράουλες", "σπόροι chia"], "Smoothie with {0}g 2% yogurt, {1}g strawberries, and {2}g chia seeds"),
        ("Φρυγανιά με {0}g ψωμί σίκαλης, {1}g μέλι και {2}g μπλούμπερι", ["ψωμί σίκαλης", "μέλι", "μπλούμπερι"], "Toast with {0}g rye bread, {1}g honey, and {2}g blueberries"),
        ("Πανκεϊκς με {0}g βρώμη, {1}g μπανάνα και {2}g βούτυρο αμυγδάλου", ["βρώμη", "μπανάνα", "βούτυρο αμυγδάλου"], "Pancakes with {0}g oats, {1}g banana, and {2}g almond butter"),
        ("Ομελέτα με {0}g αυγά, {1}g πιπεριές και {2}g ντομάτα", ["αυγά", "πιπεριές", "ντομάτα"], "Omelette with {0}g eggs, {1}g bell peppers, and {2}g tomato"),
        ("Μπολ με {0}g γιαούρτι 2%, {1}g μπλούμπερι και {2}g ξηρούς καρπούς", ["γιαούρτι 2%", "μπλούμπερι", "ξηροί καρποί (αμύγδαλα)"], "Bowl with {0}g 2% yogurt, {1}g blueberries, and {2}g nuts")
    ],
    "μεσημεριανό": [
        ("Κοτόπουλο ψητό {0}g με {1}g ρύζι καστανό και {2}g μπρόκολο στον ατμό", ["κοτόπουλο στήθος", "ρύζι καστανό", "μπρόκολο"], "Grilled chicken {0}g with {1}g brown rice and {2}g steamed broccoli"),
        ("Σολομός ψητός {0}g με {1}g κινόα και {2}g σαλάτα πιπεριές", ["σολομός", "κινόα", "πιπεριές"], "Grilled salmon {0}g with {1}g quinoa and {2}g bell pepper salad"),
        ("Μοσχαρίσια μπριζόλα {0}g με {1}g ζυμαρικά ολικής και σάλτσα {2}g ντομάτα", ["μοσχάρι (άπαχο)", "ζυμαρικά ολικής", "ντομάτα"], "Beef steak {0}g with {1}g whole wheat pasta and {2}g tomato sauce"),
        ("Σαλάτα τόνου με {0}g τόνο (κονσέρβα), {1}g πατάτες βραστές και {2}g ελαιόλαδο", ["τόνος (κονσέρβα)", "πατάτες", "ελαιόλαδο"], "Tuna salad with {0}g canned tuna, {1}g boiled potatoes, and {2}g olive oil"),
        ("Γαλοπούλα ψητή {0}g με {1}g γλυκοπατάτες ψητές και {2}g κουνουπίδι", ["γαλοπούλα", "γλυκοπατάτες", "κουνουπίδι"], "Grilled turkey {0}g with {1}g roasted sweet potatoes and {2}g cauliflower"),
        ("Μπακαλιάρος ψητός {0}g με {1}g φαγόπυρο και {2}g μελιτζάνες ψητές", ["λευκό ψάρι (μπακαλιάρος)", "φαγόπυρο", "μελιτζάνες"], "Grilled cod {0}g with {1}g buckwheat and {2}g roasted eggplant"),
        ("Ρεβίθια φούρνου {0}g με {1}g ρύζι μπασμάτι και {2}g σπανάκι σωτέ", ["ρεβίθια", "ρύζι μπασμάτι", "σπανάκι"], "Oven-baked chickpeas {0}g with {1}g basmati rice and {2}g sautéed spinach"),
        ("Σαλάτα με {0}g τυρί cottage, {1}g κοτόπουλο στήθος και {2}g ντομάτα", ["τυρί cottage", "κοτόπουλο στήθος", "ντομάτα"], "Salad with {0}g cottage cheese, {1}g chicken breast, and {2}g tomato")
    ],
    "βραδινό": [
        ("Σαλάτα με {0}g κοτόπουλο στήθος ψητό, {1}g σπανάκι και {2}g ελαιόλαδο", ["κοτόπουλο στήθος", "σπανάκι", "ελαιόλαδο"], "Salad with {0}g grilled chicken breast, {1}g spinach, and {2}g olive oil"),
        ("Σολομός ψητός {0}g με {1}g μπρόκολο στον ατμό και {2}g αβοκάντο", ["σολομός", "μπρόκολο", "αβοκάντο"], "Grilled salmon {0}g with {1}g steamed broccoli and {2}g avocado"),
        ("Ομελέτα με {0}g αυγά, {1}g πιπεριές και {2}g σπανάκι", ["αυγά", "πιπεριές", "σπανάκι"], "Omelette with {0}g eggs, {1}g bell peppers, and {2}g spinach"),
        ("Σαλάτα τόνου με {0}g τόνο (κονσέρβα), {1}g αγγούρι και {2}g ελαιόλαδο", ["τόνος (κονσέρβα)", "αγγούρι", "ελαιόλαδο"], "Tuna salad with {0}g canned tuna, {1}g cucumber, and {2}g olive oil"),
        ("Ψητή γαλοπούλα {0}g με {1}g κολοκυθάκια ψητά και {2}g καρότα", ["γαλοπούλα", "κολοκυθάκια", "καρότα"], "Grilled turkey {0}g with {1}g roasted zucchini and {2}g carrots"),
        ("Μπακαλιάρος στον ατμό {0}g με {1}g κουνουπίδι και {2}g ελαιόλαδο", ["λευκό ψάρι (μπακαλιάρος)", "κουνουπίδι", "ελαιόλαδο"], "Steamed cod {0}g with {1}g cauliflower and {2}g olive oil"),
        ("Φακές σούπα {0}g με {1}g καρότα και {2}g ντομάτα", ["φακές", "καρότα", "ντομάτα"], "Lentil soup {0}g with {1}g carrots and {2}g tomato"),
        ("Σαλάτα με {0}g τυρί cottage, {1}g ντομάτα και {2}g πιπεριές", ["τυρί cottage", "ντομάτα", "πιπεριές"], "Salad with {0}g cottage cheese, {1}g tomato, and {2}g bell peppers")
    ],
    "σνακ": [
        ("{0}g γιαούρτι 2% με {1}g μέλι και {2}g ξηρούς καρπούς", ["γιαούρτι 2%", "μέλι", "ξηροί καρποί (αμύγδαλα)"], "{0}g 2% yogurt with {1}g honey and {2}g nuts"),
        ("{0}g ψωμί ολικής με {1}g αβοκάντο", ["ψωμί ολικής", "αβοκάντο"], "{0}g whole wheat bread with {1}g avocado"),
        ("{0}g ψωμί σίκαλης με {1}g βούτυρο αμυγδάλου", ["ψωμί σίκαλης", "βούτυρο αμυγδάλου"], "{0}g rye bread with {1}g almond butter"),
        ("{0}g πορτοκάλι με {1}g φιστίκια", ["πορτοκάλι", "φιστίκια"], "{0}g orange with {1}g peanuts"),
        ("{0}g φράουλες με {1}g γιαούρτι 2%", ["φράουλες", "γιαούρτι 2%"], "{0}g strawberries with {1}g 2% yogurt"),
        ("{0}g ψωμί ολικής με {1}g ταχίνι", ["ψωμί ολικής", "ταχίνι"], "{0}g whole wheat bread with {1}g tahini"),
        ("{0}g μπανάνα με {1}g ξηρούς καρπούς", ["μπανάνα", "ξηροί καρποί (αμύγδαλα)"], "{0}g banana with {1}g nuts"),
        ("{0}g μήλο με {1}g φιστίκια", ["μήλο", "φιστίκια"], "{0}g apple with {1}g peanuts")
    ]
}

def calculate_meal_calories(ingredients, quantities):
    total_calories = 0
    for food, qty in zip(ingredients, quantities):
        category = next(c for c, foods in food_data.items() if food in foods)
        protein = food_data[category][food]["protein"] * (qty / 100)
        carbs = food_data[category][food]["carbs"] * (qty / 100)
        fat = food_data[category][food]["fat"] * (qty / 100)
        total_calories += (protein * 4) + (carbs * 4) + (fat * 9)
    return round(total_calories)

def get_food_suggestions(meal_type, lang="el"):
    recipe_tuple = random.choice(recipes[meal_type])
    recipe_el, ingredients, recipe_en = recipe_tuple
    quantities = [food_data[next(c for c, foods in food_data.items() if food in foods)][food]["portion"] for food in ingredients]
    calories = calculate_meal_calories(ingredients, quantities)
    recipe = recipe_el if lang == "el" else recipe_en
    return recipe.format(*quantities), calories

def create_meal_plan(target_calories, lang="el"):
    days = translations[lang]["days"]
    meal_types = ["πρωινό", "σνακ1", "μεσημεριανό", "σνακ2", "βραδινό"]
    meal_plan = {}
    
    for day in days:
        daily_calories = random.uniform(target_calories * 0.9, target_calories * 1.1)
        meal_calories = {
            "πρωινό": daily_calories * random.uniform(0.23, 0.27),
            "σνακ1": daily_calories * random.uniform(0.08, 0.12),
            "μεσημεριανό": daily_calories * random.uniform(0.28, 0.32),
            "σνακ2": daily_calories * random.uniform(0.08, 0.12),
            "βραδινό": daily_calories * random.uniform(0.23, 0.27)
        }
        meal_plan[day] = {}
        for meal_type in meal_types:
            food_suggestion_meal_type = "σνακ" if meal_type in ["σνακ1", "σνακ2"] else meal_type
            recipe, actual_calories = get_food_suggestions(food_suggestion_meal_type, lang)
            meal_plan[day][meal_type] = {
                "θερμίδες": round(meal_calories[meal_type]),
                "συνταγή": recipe
            }
    return meal_plan

def wrap_text(text, font, max_width):
    lines = []
    words = text.split(" ")
    current_line = ""
    
    for word in words:
        test_line = current_line + " " + word if current_line else word
        width = font.getlength(test_line)
        if width <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    return lines

def save_plan_to_jpeg(meal_plan, user_info, lang="el"):
    filename = QFileDialog.getSaveFileName(None, "Save as Image" if lang == "en" else "Αποθήκευση ως Εικόνα", "", "JPEG files (*.jpg)")[0]
    if not filename: return
    width, height = 1920, 1080
    img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(img)
    try:
        font_title = ImageFont.truetype("arial.ttf", 30)
        font_text = ImageFont.truetype("arial.ttf", 14)
    except:
        font_title = ImageFont.load_default()
        font_text = ImageFont.load_default()

    draw.text((width // 2 - 250, 20), translations[lang]["plan_title"], font=font_title, fill="#1976D2")
    user_info_text = f"{translations[lang]['goal_info']}: {user_info['goal']} | {translations[lang]['calories_info']}: {user_info['calories']} kcal\n{translations[lang]['protein_info']}: {user_info['protein']}g | {translations[lang]['carbs_info']}: {user_info['carbs']}g | {translations[lang]['fat_info']}: {user_info['fat']}g\n{translations[lang]['created_info']}: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
    draw.text((50, 70), user_info_text, font=font_text, fill="#424242")
    
    col_width, row_height, start_x, start_y = 274, 150, 0, 150
    days = list(meal_plan.keys())
    meal_types = ["πρωινό", "σνακ1", "μεσημεριανό", "σνακ2", "βραδινό"]
    header_colors = ["#FFCDD2", "#C8E6C9", "#BBDEFB", "#F8BBD0", "#C5CAE9", "#B2EBF2", "#D1C4E9"]
    
    for col, day in enumerate(days):
        draw.rectangle([(start_x + col * col_width, start_y), (start_x + (col + 1) * col_width, start_y + 40)], fill=header_colors[col])
        draw.text((start_x + col * col_width + 10, start_y + 10), day, font=font_text, fill="#424242")
        if col < len(days) - 1:
            draw.line([(start_x + (col + 1) * col_width, start_y), (start_x + (col + 1) * col_width, start_y + 40 + len(meal_types) * row_height)], fill="#E0E0E0", width=1)
    
    for row, meal_type in enumerate(meal_types):
        draw.line([(start_x, start_y + 40 + row * row_height), (start_x + 7 * col_width, start_y + 40 + row * row_height)], fill="#E0E0E0", width=1)
        for col, day in enumerate(days):
            display_meal = f"{translations[lang]['meals'][meal_type]}\n{meal_plan[day][meal_type]['θερμίδες']} kcal\n{meal_plan[day][meal_type]['συνταγή']}"
            lines = display_meal.split("\n")
            y_offset = start_y + 50 + row * row_height
            for line in lines:
                wrapped_lines = wrap_text(line, font_text, col_width - 20)
                for wrapped_line in wrapped_lines:
                    draw.text((start_x + col * col_width + 10, y_offset), wrapped_line, font=font_text, fill="#424242")
                    y_offset += 20
    
    draw.line([(start_x, start_y + 40 + len(meal_types) * row_height), (start_x + 7 * col_width, start_y + 40 + len(meal_types) * row_height)], fill="#E0E0E0", width=1)
    img.save(filename, "JPEG")

class DietApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_lang = "el"
        self.setWindowTitle(translations[self.current_lang]["title"])
        self.setGeometry(100, 100, 1920, 1080)  # Larger window for a more spacious feel
        self.setStyleSheet("""
            background-color: #F2F2F7;  /* Light gray, Apple-like */
        """)

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Left Panel (Input Area)
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(25)  # More breathing room
        left_layout.setContentsMargins(40, 40, 40, 40)  # Larger padding
        left_panel.setStyleSheet("""
            background-color: rgba(255, 255, 255, 0.8);  /* Semi-transparent white */
            border-radius: 20px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);  /* Soft shadow */
            backdrop-filter: blur(10px);  /* Blurred background effect */
        """)  # Glossy, blurred Apple-style effect
        left_panel.setFixedWidth(450)  # Wider panel for a modern layout
        left_panel.setMinimumHeight(800)  # Full height for a fluid feel

        self.title_label = QLabel(translations[self.current_lang]["title"])
        self.title_label.setFont(QFont("SF Pro Display", 36, QFont.Weight.Bold))  # Apple-like font
        self.title_label.setStyleSheet("color: #1A1A1A;")  # Darker text for contrast
        left_layout.addWidget(self.title_label, alignment=Qt.AlignmentFlag.AlignLeft)

        self.inputs = {}
        self.labels = {}
        for label_key, var_name, type_, options_key in [
            ("goal_label", "goal", "combo", "goals"),
            ("weight_label", "weight", "entry", ""),
            ("height_label", "height", "entry", ""),
            ("age_label", "age", "entry", ""),
            ("gender_label", "gender", "combo", "genders"),
            ("activity_label", "activity", "combo", "activities")
        ]:
            input_layout = QHBoxLayout()
            input_layout.setSpacing(15)
            label_widget = QLabel(translations[self.current_lang][label_key])
            label_widget.setFont(QFont("SF Pro Display", 14))  # Modern font
            label_widget.setStyleSheet("color: #3C3C43;")  # Subtle dark gray
            self.labels[var_name] = label_widget
            input_layout.addWidget(label_widget)
            if type_ == "entry":
                entry = QLineEdit()
                entry.setStyleSheet("""
                    background-color: #FFFFFF;
                    color: #000000;
                    border: none;
                    padding: 12px;
                    border-radius: 12px;
                    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
                """)  # Flat, glossy input
                self.inputs[var_name] = entry
                input_layout.addWidget(entry)
            else:
                combo = QComboBox()
                combo.addItems(translations[self.current_lang][options_key])
                combo.setStyleSheet("""
                    background-color: #FFFFFF;
                    color: #000000;
                    padding: 12px;
                    border: none;
                    border-radius: 12px;
                    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
                """)
                self.inputs[var_name] = combo
                input_layout.addWidget(combo)
            left_layout.addLayout(input_layout)

        # Action Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(20)
        self.calculate_btn = QPushButton(translations[self.current_lang]["calculate_btn"])
        self.calculate_btn.setFont(QFont("SF Pro Display", 14, QFont.Weight.Bold))
        self.calculate_btn.setStyleSheet("""
            background-color: #007AFF;  /* Apple blue */
            color: #FFFFFF;
            padding: 15px;
            border-radius: 15px;
            border: none;
            box-shadow: 0 4px 12px rgba(0, 122, 255, 0.3);
        """)  # Glossy, flat button
        self.calculate_btn.clicked.connect(self.calculate_plan)
        button_layout.addWidget(self.calculate_btn)

        self.save_btn = QPushButton(translations[self.current_lang]["save_btn"])
        self.save_btn.setFont(QFont("SF Pro Display", 14, QFont.Weight.Bold))
        self.save_btn.setStyleSheet("""
            background-color: #007AFF;
            color: #FFFFFF;
            padding: 15px;
            border-radius: 15px;
            border: none;
            box-shadow: 0 4px 12px rgba(0, 122, 255, 0.3);
        """)
        self.save_btn.setEnabled(False)
        self.save_btn.clicked.connect(self.save_plan)
        button_layout.addWidget(self.save_btn)
        left_layout.addLayout(button_layout)

        # Language Buttons
        lang_layout = QHBoxLayout()
        self.lang_gr_btn = QPushButton("GR")
        self.lang_gr_btn.setFont(QFont("SF Pro Display", 12, QFont.Weight.Bold))
        self.lang_gr_btn.setFixedSize(60, 40)
        self.lang_gr_btn.setStyleSheet("""
            background-color: #FFFFFF;
            color: #007AFF;
            border: none;
            border-radius: 10px;
            padding: 5px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        """)
        self.lang_gr_btn.clicked.connect(lambda: self.switch_language("el"))
        lang_layout.addWidget(self.lang_gr_btn)

        self.lang_en_btn = QPushButton("EN")
        self.lang_en_btn.setFont(QFont("SF Pro Display", 12, QFont.Weight.Bold))
        self.lang_en_btn.setFixedSize(60, 40)
        self.lang_en_btn.setStyleSheet("""
            background-color: #FFFFFF;
            color: #007AFF;
            border: none;
            border-radius: 10px;
            padding: 5px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        """)
        self.lang_en_btn.clicked.connect(lambda: self.switch_language("en"))
        lang_layout.addWidget(self.lang_en_btn)
        lang_layout.addStretch()
        left_layout.addLayout(lang_layout)

        self.info_label = QLabel(translations[self.current_lang]["info_default"])
        self.info_label.setFont(QFont("SF Pro Display", 12))
        self.info_label.setStyleSheet("color: #8E8E93;")  # Light gray for info
        self.info_label.setWordWrap(True)
        left_layout.addWidget(self.info_label)
        left_layout.addStretch()

        main_layout.addWidget(left_panel)

        # Scroll Area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("background-color: #FFFFFF; border: none;")
        self.plan_widget = QWidget()
        self.plan_layout = QGridLayout(self.plan_widget)
        self.plan_layout.setSpacing(0)
        self.plan_widget.setStyleSheet("background-color: #FFFFFF;")
        self.scroll_area.setWidget(self.plan_widget)
        self.scroll_area.setVisible(False)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setFixedWidth(1470)  # Adjusted for wider left panel
        main_layout.addWidget(self.scroll_area)

    def switch_language(self, lang):
        try:
            if self.current_lang != lang:
                self.current_lang = lang
                self.update_ui()
                self.info_label.setText(f"Language switched to {'Greek' if lang == 'el' else 'English'}")
                self.info_label.setStyleSheet("color: #34C759;")  # Green for success
        except Exception as e:
            self.info_label.setText(translations[self.current_lang]["error_general"].format(str(e)))
            self.info_label.setStyleSheet("color: #FF3B30;")  # Red for error

    def update_ui(self):
        try:
            lang = self.current_lang
            self.setWindowTitle(translations[lang]["title"])
            self.title_label.setText(translations[lang]["title"])
            for var_name, label in self.labels.items():
                label.setText(translations[lang][f"{var_name}_label"])
            for var_name in ["goal", "gender", "activity"]:
                combo = self.inputs.get(var_name)
                if combo:
                    current_text = combo.currentText()
                    combo.clear()
                    combo.addItems(translations[lang][f"{var_name}s"])
                    index = combo.findText(current_text)
                    if index >= 0:
                        combo.setCurrentIndex(index)
            self.calculate_btn.setText(translations[lang]["calculate_btn"])
            self.save_btn.setText(translations[lang]["save_btn"])
            if "Error" not in self.info_label.text() and "Σφάλμα" not in self.info_label.text():
                self.info_label.setText(translations[lang]["info_default"])
            if self.scroll_area.isVisible():
                self.calculate_plan()
        except Exception as e:
            self.info_label.setText(translations[lang]["error_general"].format(str(e)))
            self.info_label.setStyleSheet("color: #FF3B30;")

    def calculate_plan(self):
        try:
            lang = self.current_lang
            goal = self.inputs["goal"].currentText()
            weight_text = self.inputs["weight"].text().strip()
            height_text = self.inputs["height"].text().strip()
            age_text = self.inputs["age"].text().strip()
            gender = self.inputs["gender"].currentText()
            activity = self.inputs["activity"].currentText()

            if not weight_text or not height_text or not age_text:
                self.info_label.setText(translations[lang]["error_fields"])
                self.info_label.setStyleSheet("color: #FF3B30;")
                return

            weight = float(weight_text)
            height = float(height_text)
            age = int(age_text)

            if weight <= 0 or height <= 0 or age <= 0:
                self.info_label.setText(translations[lang]["error_positive"])
                self.info_label.setStyleSheet("color: #FF3B30;")
                return

            bmr = calculate_bmr(weight, height, age, gender)
            tdee = calculate_tdee(bmr, activity)
            target_calories = calculate_target_calories(tdee, goal)
            macro_ratio = [40, 30, 30] if goal in ["Απώλεια", "Loss"] else [30, 50, 20] if goal in ["Μυϊκή Αύξηση", "Muscle Gain"] else [30, 40, 30]
            macros = calculate_macros(target_calories, macro_ratio)
            meal_plan = create_meal_plan(target_calories, lang)

            for i in reversed(range(self.plan_layout.count())):
                widget = self.plan_layout.itemAt(i).widget()
                if widget:
                    widget.setParent(None)

            days = translations[lang]["days"]
            header_colors = ["#FFCDD2", "#C8E6C9", "#BBDEFB", "#F8BBD0", "#C5CAE9", "#B2EBF2", "#D1C4E9"]
            column_width = 210  # Adjusted for wider scroll area
            for col, day in enumerate(days):
                day_label = QLabel(day)
                day_label.setFont(QFont("SF Pro Display", 14, QFont.Weight.Bold))
                day_label.setStyleSheet(f"background-color: {header_colors[col]}; color: #000000; padding: 10px; border-right: 1px solid #E0E0E0;")
                day_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                day_label.setFixedWidth(column_width)
                self.plan_layout.addWidget(day_label, 0, col)

            meal_types = ["πρωινό", "σνακ1", "μεσημεριανό", "σνακ2", "βραδινό"]
            for row, meal_type in enumerate(meal_types):
                for col, day in enumerate(days):
                    display_meal = translations[lang]["meals"][meal_type]
                    meal_card = QWidget()
                    meal_card.setStyleSheet("background-color: #FFFFFF; border-bottom: 1px solid #E0E0E0; border-right: 1px solid #E0E0E0; padding: 5px;")
                    meal_layout = QVBoxLayout(meal_card)
                    meal_title = QLabel(f"{display_meal} - {meal_plan[day][meal_type]['θερμίδες']} kcal")
                    meal_title.setFont(QFont("SF Pro Display", 9, QFont.Weight.Bold))
                    meal_title.setStyleSheet("color: #000000;")
                    meal_layout.addWidget(meal_title)
                    meal_recipe = QLabel(meal_plan[day][meal_type]["συνταγή"])
                    meal_recipe.setFont(QFont("SF Pro Display", 9))
                    meal_recipe.setStyleSheet("color: #8E8E93;")
                    meal_recipe.setWordWrap(True)
                    meal_layout.addWidget(meal_recipe)
                    meal_card.setFixedWidth(column_width)
                    meal_card.setMinimumHeight(100)
                    self.plan_layout.addWidget(meal_card, row + 1, col)

            self.scroll_area.setVisible(True)
            self.animation = QPropertyAnimation(self.scroll_area, b"windowOpacity")
            self.animation.setDuration(500)
            self.animation.setStartValue(0.0)
            self.animation.setEndValue(1.0)
            self.animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
            self.animation.start()

            info_text = f"{translations[lang]['calories_info']}: {int(target_calories)} kcal\nBMR: {int(bmr)} kcal | TDEE: {int(tdee)} kcal\nP: {macros['πρωτεΐνη']}g | C: {macros['υδατάνθρακες']}g | F: {macros['λίπος']}g"
            self.info_label.setText(info_text)
            self.info_label.setStyleSheet("color: #34C759;")
            self.user_info = {"goal": goal, "calories": int(target_calories), "protein": macros["πρωτεΐνη"], "carbs": macros["υδατάνθρακες"], "fat": macros["λίπος"]}
            self.save_btn.setEnabled(True)

        except ValueError as ve:
            self.info_label.setText(translations[lang]["error_numbers"].format(str(ve)))
            self.info_label.setStyleSheet("color: #FF3B30;")
        except Exception as e:
            self.info_label.setText(translations[lang]["error_general"].format(str(e)))
            self.info_label.setStyleSheet("color: #FF3B30;")

    def save_plan(self):
        try:
            lang = self.current_lang
            meal_plan = create_meal_plan(self.user_info["calories"], lang)
            save_plan_to_jpeg(meal_plan, self.user_info, lang)
            self.info_label.setText(translations[lang]["saved"])
            self.info_label.setStyleSheet("color: #34C759;")
        except Exception as e:
            self.info_label.setText(translations[lang]["error_save"].format(str(e)))
            self.info_label.setStyleSheet("color: #FF3B30;")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setFont(QFont("SF Pro Display", 12))  # Default modern font
    palette = app.palette()
    palette.setColor(QPalette.ColorRole.Window, QColor("#F2F2F7"))
    palette.setColor(QPalette.ColorRole.WindowText, QColor("#000000"))
    app.setPalette(palette)
    window = DietApp()
    window.showMaximized()
    sys.exit(app.exec())