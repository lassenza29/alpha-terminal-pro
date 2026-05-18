#!/usr/bin/env python3
"""
Todo List Application with Local Storage
A modern, feature-rich todo application with persistent local storage
"""

import streamlit as st
import json
import os
from datetime import datetime
from typing import List, Dict, Optional
import pandas as pd

# ============================================================================
# PAGE CONFIG & THEME
# ============================================================================

st.set_page_config(
    page_title="Todo List Pro",
    page_icon="✅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Dark Mode Custom CSS
st.markdown("""
<style>
    * {
        margin: 0;
        padding: 0;
    }
    
    body, [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
        color: #e0e7ff;
    }
    
    [data-testid="stSidebar"] {
        background-color: #1a1632 !important;
    }
    
    .header-title {
        color: #818cf8;
        font-size: 42px;
        font-weight: bold;
        text-align: center;
        margin: 30px 0 10px 0;
        text-shadow: 0 0 20px rgba(129, 140, 248, 0.3);
    }
    
    .subtitle {
        color: #a5b4fc;
        font-size: 14px;
        text-align: center;
        margin-bottom: 30px;
    }
    
    .todo-card {
        background: linear-gradient(135deg, #1e1b4b 0%, #312e81 100%);
        border: 1px solid #4c1d95;
        border-radius: 12px;
        padding: 16px;
        margin: 10px 0;
        transition: all 0.3s ease;
    }
    
    .todo-card:hover {
        border-color: #818cf8;
        box-shadow: 0 0 15px rgba(129, 140, 248, 0.2);
    }
    
    .todo-title {
        color: #e0e7ff;
        font-size: 16px;
        font-weight: 600;
        margin-bottom: 8px;
    }
    
    .todo-description {
        color: #c7d2fe;
        font-size: 13px;
        margin-bottom: 10px;
        font-style: italic;
    }
    
    .todo-meta {
        display: flex;
        gap: 10px;
        flex-wrap: wrap;
        margin-top: 10px;
    }
    
    .priority-high {
        background-color: #dc2626;
        color: white;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 11px;
        font-weight: bold;
    }
    
    .priority-medium {
        background-color: #f59e0b;
        color: white;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 11px;
        font-weight: bold;
    }
    
    .priority-low {
        background-color: #10b981;
        color: white;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 11px;
        font-weight: bold;
    }
    
    .status-completed {
        color: #6ee7b7;
        font-size: 11px;
        font-weight: bold;
        text-decoration: line-through;
    }
    
    .status-pending {
        color: #fbbf24;
        font-size: 11px;
        font-weight: bold;
    }
    
    .category-badge {
        background-color: #6366f1;
        color: white;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 11px;
    }
    
    .category-work {
        background-color: #3b82f6;
    }
    
    .category-personal {
        background-color: #ec4899;
    }
    
    .category-shopping {
        background-color: #f59e0b;
    }
    
    .category-health {
        background-color: #10b981;
    }
    
    .category-other {
        background-color: #8b5cf6;
    }
    
    .input-section {
        background: linear-gradient(135deg, #1e1b4b 0%, #2d1b69 100%);
        border: 1px solid #4c1d95;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
    }
    
    .stats-card {
        background: linear-gradient(135deg, #312e81 0%, #4c1d95 100%);
        border-left: 4px solid #818cf8;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
    }
    
    .stats-number {
        color: #818cf8;
        font-size: 24px;
        font-weight: bold;
    }
    
    .stats-label {
        color: #a5b4fc;
        font-size: 12px;
        margin-top: 5px;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #818cf8 0%, #6366f1 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #a5b4fc 0%, #818cf8 100%);
        box-shadow: 0 0 15px rgba(129, 140, 248, 0.4);
    }
    
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > select {
        background-color: #0f172a !important;
        color: #e0e7ff !important;
        border: 1px solid #4c1d95 !important;
        border-radius: 8px !important;
    }
    
    .stCheckbox > label {
        color: #e0e7ff !important;
    }
    
    .success-box {
        background-color: rgba(16, 185, 129, 0.1);
        border: 1px solid #10b981;
        border-radius: 8px;
        padding: 12px;
        color: #6ee7b7;
        margin: 10px 0;
    }
    
    .warning-box {
        background-color: rgba(245, 158, 11, 0.1);
        border: 1px solid #f59e0b;
        border-radius: 8px;
        padding: 12px;
        color: #fcd34d;
        margin: 10px 0;
    }
    
    .error-box {
        background-color: rgba(220, 38, 38, 0.1);
        border: 1px solid #dc2626;
        border-radius: 8px;
        padding: 12px;
        color: #fca5a5;
        margin: 10px 0;
    }
    
    .empty-state {
        text-align: center;
        padding: 40px;
        color: #6b7280;
    }
    
    .empty-state-icon {
        font-size: 48px;
        margin-bottom: 10px;
    }
    
    .tab-separator {
        color: #4c1d95;
        margin: 20px 0;
        border-top: 1px solid #4c1d95;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# LOCAL STORAGE FUNCTIONS
# ============================================================================

DATA_FILE = "todos.json"

def load_todos() -> List[Dict]:
    """Load todos from local storage"""
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    except Exception as e:
        st.error(f"❌ Erreur lors du chargement: {str(e)}")
        return []

def save_todos(todos: List[Dict]) -> bool:
    """Save todos to local storage"""
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(todos, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        st.error(f"❌ Erreur lors de la sauvegarde: {str(e)}")
        return False

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def generate_todo_id() -> str:
    """Generate unique todo ID"""
    return str(int(datetime.now().timestamp() * 1000))

def get_priority_color(priority: str) -> str:
    """Get HTML color for priority"""
    colors = {
        "Haute": "#dc2626",
        "Moyenne": "#f59e0b",
        "Basse": "#10b981"
    }
    return colors.get(priority, "#6b7280")

def get_category_class(category: str) -> str:
    """Get CSS class for category"""
    classes = {
        "Travail": "category-work",
        "Personnel": "category-personal",
        "Courses": "category-shopping",
        "Santé": "category-health",
        "Autre": "category-other"
    }
    return classes.get(category, "category-other")

def format_date(date_str: str) -> str:
    """Format date for display"""
    if not date_str:
        return "Pas de date"
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        return date_obj.strftime("%d/%m/%Y")
    except:
        return date_str

# ============================================================================
# TODO OPERATIONS
# ============================================================================

def add_todo(title: str, description: str, category: str, priority: str, due_date: str) -> bool:
    """Add a new todo"""
    todos = load_todos()
    
    new_todo = {
        "id": generate_todo_id(),
        "title": title,
        "description": description,
        "category": category,
        "priority": priority,
        "due_date": due_date,
        "completed": False,
        "created_at": datetime.now().isoformat(),
        "completed_at": None
    }
    
    todos.append(new_todo)
    return save_todos(todos)

def update_todo(todo_id: str, **kwargs) -> bool:
    """Update a todo"""
    todos = load_todos()
    
    for todo in todos:
        if todo["id"] == todo_id:
            for key, value in kwargs.items():
                todo[key] = value
            return save_todos(todos)
    
    return False

def delete_todo(todo_id: str) -> bool:
    """Delete a todo"""
    todos = load_todos()
    todos = [todo for todo in todos if todo["id"] != todo_id]
    return save_todos(todos)

def toggle_todo_status(todo_id: str) -> bool:
    """Toggle todo completion status"""
    todos = load_todos()
    
    for todo in todos:
        if todo["id"] == todo_id:
            todo["completed"] = not todo["completed"]
            todo["completed_at"] = datetime.now().isoformat() if todo["completed"] else None
            return save_todos(todos)
    
    return False

def get_statistics() -> Dict:
    """Get todo statistics"""
    todos = load_todos()
    
    total = len(todos)
    completed = sum(1 for t in todos if t["completed"])
    pending = total - completed
    high_priority = sum(1 for t in todos if t["priority"] == "Haute" and not t["completed"])
    overdue = sum(1 for t in todos if t["due_date"] and t["due_date"] < datetime.now().strftime("%Y-%m-%d") and not t["completed"])
    
    return {
        "total": total,
        "completed": completed,
        "pending": pending,
        "completion_rate": (completed / total * 100) if total > 0 else 0,
        "high_priority": high_priority,
        "overdue": overdue
    }

def filter_todos(todos: List[Dict], filter_type: str, search: str = "") -> List[Dict]:
    """Filter todos based on criteria"""
    filtered = todos
    
    # Filter by status
    if filter_type == "Complétés":
        filtered = [t for t in filtered if t["completed"]]
    elif filter_type == "En attente":
        filtered = [t for t in filtered if not t["completed"]]
    elif filter_type == "Haute priorité":
        filtered = [t for t in filtered if t["priority"] == "Haute" and not t["completed"]]
    elif filter_type == "En retard":
        today = datetime.now().strftime("%Y-%m-%d")
        filtered = [t for t in filtered if t["due_date"] and t["due_date"] < today and not t["completed"]]
    
    # Search filter
    if search:
        search_lower = search.lower()
        filtered = [
            t for t in filtered 
            if search_lower in t["title"].lower() or search_lower in t["description"].lower()
        ]
    
    return filtered

def sort_todos(todos: List[Dict], sort_by: str) -> List[Dict]:
    """Sort todos based on criteria"""
    if sort_by == "Priorité (Haute → Basse)":
        priority_order = {"Haute": 0, "Moyenne": 1, "Basse": 2}
        return sorted(todos, key=lambda x: (x["completed"], priority_order.get(x["priority"], 3)))
    elif sort_by == "Date limite (Proche → Loin)":
        return sorted(todos, key=lambda x: (x["completed"], x["due_date"] or "9999-12-31"))
    elif sort_by == "Récents d'abord":
        return sorted(todos, key=lambda x: x["created_at"], reverse=True)
    elif sort_by == "Anciens d'abord":
        return sorted(todos, key=lambda x: x["created_at"])
    
    return todos

# ============================================================================
# DISPLAY FUNCTIONS
# ============================================================================

def display_todo_card(todo: Dict) -> None:
    """Display a single todo card"""
    col1, col2, col3, col4 = st.columns([0.05, 1, 0.15, 0.15])
    
    with col1:
        # Checkbox to mark as complete
        new_status = st.checkbox(
            "✓",
            value=todo["completed"],
            key=f"checkbox_{todo['id']}",
            label_visibility="collapsed"
        )
        if new_status != todo["completed"]:
            toggle_todo_status(todo["id"])
            st.rerun()
    
    with col2:
        # Todo content
        status_class = "status-completed" if todo["completed"] else "status-pending"
        status_text = "✓ Complété" if todo["completed"] else "⏳ En attente"
        
        st.markdown(f"""
        <div class="todo-card">
            <div class="todo-title" style="{'text-decoration: line-through; opacity: 0.6;' if todo['completed'] else ''}">
                {todo['title']}
            </div>
            {'<div class="todo-description">' + todo['description'] + '</div>' if todo['description'] else ''}
            <div class="todo-meta">
                <span class="priority-{todo['priority'].lower() if todo['priority'] == 'Basse' else 'high' if todo['priority'] == 'Haute' else 'medium'}">
                    {todo['priority']}
                </span>
                <span class="category-badge {get_category_class(todo['category'])}">
                    {todo['category']}
                </span>
                <span class="{status_class}">{status_text}</span>
                {'<span style="color: #818cf8; font-size: 11px;">📅 ' + format_date(todo['due_date']) + '</span>' if todo['due_date'] else ''}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        # Edit button
        if st.button("✏️ Modifier", key=f"edit_{todo['id']}", use_container_width=True):
            st.session_state.edit_mode = True
            st.session_state.edit_todo_id = todo["id"]
            st.rerun()
    
    with col4:
        # Delete button
        if st.button("🗑️ Supprimer", key=f"delete_{todo['id']}", use_container_width=True):
            delete_todo(todo["id"])
            st.rerun()

def display_statistics() -> None:
    """Display statistics cards"""
    stats = get_statistics()
    
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    with col1:
        st.markdown(f"""
        <div class="stats-card">
            <div class="stats-number">{stats['total']}</div>
            <div class="stats-label">TOTAL</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="stats-card">
            <div class="stats-number">{stats['completed']}</div>
            <div class="stats-label">COMPLÉTÉS</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="stats-card">
            <div class="stats-number">{stats['pending']}</div>
            <div class="stats-label">EN ATTENTE</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="stats-card">
            <div class="stats-number">{stats['completion_rate']:.0f}%</div>
            <div class="stats-label">PROGRESSION</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col5:
        st.markdown(f"""
        <div class="stats-card">
            <div class="stats-number">{stats['high_priority']}</div>
            <div class="stats-label">HAUTE PRIORITÉ</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col6:
        st.markdown(f"""
        <div class="stats-card">
            <div class="stats-number">{stats['overdue']}</div>
            <div class="stats-label">EN RETARD</div>
        </div>
        """, unsafe_allow_html=True)

# ============================================================================
# EXPORT/IMPORT FUNCTIONS
# ============================================================================

def export_todos_csv() -> str:
    """Export todos to CSV format"""
    todos = load_todos()
    
    if not todos:
        return ""
    
    df = pd.DataFrame(todos)
    df = df[["title", "description", "category", "priority", "due_date", "completed", "created_at"]]
    df["due_date"] = df["due_date"].apply(format_date)
    df["completed"] = df["completed"].map({True: "Oui", False: "Non"})
    
    return df.to_csv(index=False, encoding='utf-8')

def export_todos_json() -> str:
    """Export todos to JSON format"""
    todos = load_todos()
    return json.dumps(todos, ensure_ascii=False, indent=2)

# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    """Main application"""
    
    # Initialize session state
    if "edit_mode" not in st.session_state:
        st.session_state.edit_mode = False
    if "edit_todo_id" not in st.session_state:
        st.session_state.edit_todo_id = None
    
    # Header
    st.markdown('<div class="header-title">✅ Todo List Pro</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Organisez vos tâches avec efficacité | Stockage local persistent</div>', unsafe_allow_html=True)
    
    # Statistics
    st.markdown("### 📊 Vue d'ensemble")
    display_statistics()
    st.markdown('<div class="tab-separator"></div>', unsafe_allow_html=True)
    
    # Main tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📝 Ajouter une tâche", "📋 Mes tâches", "📈 Analyse", "⚙️ Paramètres"])
    
    # ===== TAB 1: ADD TODO =====
    with tab1:
        st.markdown("### Ajouter une nouvelle tâche")
        
        with st.container(border=True):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                title = st.text_input(
                    "Titre de la tâche *",
                    placeholder="Ex: Terminer le rapport...",
                    label_visibility="collapsed"
                )
            
            with col2:
                priority = st.selectbox(
                    "Priorité",
                    ["Basse", "Moyenne", "Haute"],
                    label_visibility="collapsed"
                )
            
            description = st.text_area(
                "Description (optionnel)",
                placeholder="Ajouter plus de détails...",
                height=100,
                label_visibility="collapsed"
            )
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                category = st.selectbox(
                    "Catégorie",
                    ["Travail", "Personnel", "Courses", "Santé", "Autre"],
                    label_visibility="collapsed"
                )
            
            with col2:
                due_date = st.date_input(
                    "Date limite (optionnel)",
                    value=None,
                    label_visibility="collapsed"
                )
            
            with col3:
                st.markdown("")  # Spacer
            
            col1, col2, col3 = st.columns([1, 1, 2])
            
            with col1:
                if st.button("✅ Ajouter la tâche", use_container_width=True):
                    if not title.strip():
                        st.error("❌ Le titre est obligatoire!")
                    else:
                        due_date_str = due_date.strftime("%Y-%m-%d") if due_date else ""
                        if add_todo(title, description, category, priority, due_date_str):
                            st.success("✅ Tâche ajoutée avec succès!")
                            st.rerun()
                        else:
                            st.error("❌ Erreur lors de l'ajout")
            
            with col2:
                if st.button("🔄 Réinitialiser", use_container_width=True):
                    st.rerun()
    
    # ===== TAB 2: TODOS LIST =====
    with tab2:
        st.markdown("### Mes tâches")
        
        # Filters and search
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            filter_type = st.selectbox(
                "Filtrer par:",
                ["Tous", "En attente", "Complétés", "Haute priorité", "En retard"],
                label_visibility="collapsed"
            )
        
        with col2:
            sort_by = st.selectbox(
                "Trier par:",
                ["Priorité (Haute → Basse)", "Date limite (Proche → Loin)", "Récents d'abord", "Anciens d'abord"],
                label_visibility="collapsed"
            )
        
        with col3:
            search = st.text_input(
                "Rechercher...",
                placeholder="Titre ou description",
                label_visibility="collapsed"
            )
        
        st.markdown('<div class="tab-separator"></div>', unsafe_allow_html=True)
        
        # Load and display todos
        todos = load_todos()
        
        if not todos:
            st.markdown("""
            <div class="empty-state">
                <div class="empty-state-icon">📭</div>
                <div>Aucune tâche pour le moment</div>
                <div style="color: #6b7280; font-size: 12px; margin-top: 10px;">
                    Allez à l'onglet "Ajouter une tâche" pour commencer!
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Apply filters and sort
            filtered_todos = filter_todos(todos, filter_type, search)
            sorted_todos = sort_todos(filtered_todos, sort_by)
            
            if not sorted_todos:
                st.info("❌ Aucune tâche ne correspond à vos critères")
            else:
                st.markdown(f"**{len(sorted_todos)}** tâche(s) trouvée(s)")
                st.markdown('<div class="tab-separator"></div>', unsafe_allow_html=True)
                
                for todo in sorted_todos:
                    display_todo_card(todo)
    
    # ===== TAB 3: ANALYTICS =====
    with tab3:
        st.markdown("### 📈 Analyse des tâches")
        
        todos = load_todos()
        
        if not todos:
            st.info("Aucune tâche pour afficher les statistiques")
        else:
            # Category breakdown
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Tâches par catégorie")
                category_counts = {}
                for todo in todos:
                    category = todo["category"]
                    category_counts[category] = category_counts.get(category, 0) + 1
                
                df_categories = pd.DataFrame(
                    list(category_counts.items()),
                    columns=["Catégorie", "Nombre"]
                )
                
                st.bar_chart(df_categories.set_index("Catégorie"))
            
            with col2:
                st.markdown("#### Tâches par priorité")
                priority_counts = {}
                for todo in todos:
                    priority = todo["priority"]
                    priority_counts[priority] = priority_counts.get(priority, 0) + 1
                
                df_priority = pd.DataFrame(
                    list(priority_counts.items()),
                    columns=["Priorité", "Nombre"]
                )
                
                st.bar_chart(df_priority.set_index("Priorité"))
            
            st.markdown("---")
            
            # Completion trend
            st.markdown("#### Status des tâches")
            completed_count = sum(1 for t in todos if t["completed"])
            pending_count = len(todos) - completed_count
            
            df_status = pd.DataFrame({
                "Status": ["Complétés", "En attente"],
                "Nombre": [completed_count, pending_count]
            })
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.markdown(f"**Complétés:** {completed_count} ({completed_count/len(todos)*100:.1f}%)")
                st.progress(completed_count / len(todos) if len(todos) > 0 else 0)
            
            with col2:
                st.markdown(f"**En attente:** {pending_count} ({pending_count/len(todos)*100:.1f}%)")
                st.progress(pending_count / len(todos) if len(todos) > 0 else 0)
            
            st.markdown("---")
            
            # High priority tasks
            st.markdown("#### Tâches à haute priorité")
            high_priority = [t for t in todos if t["priority"] == "Haute"]
            
            if high_priority:
                for todo in high_priority[:5]:
                    status = "✓" if todo["completed"] else "⏳"
                    st.write(f"{status} **{todo['title']}** - {format_date(todo['due_date'])}")
            else:
                st.info("Aucune tâche à haute priorité")
    
    # ===== TAB 4: SETTINGS =====
    with tab4:
        st.markdown("### ⚙️ Paramètres et Export")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📥 Exporter les données")
            
            export_type = st.radio(
                "Format d'export:",
                ["CSV", "JSON"],
                label_visibility="collapsed"
            )
            
            if export_type == "CSV":
                csv_data = export_todos_csv()
                if csv_data:
                    st.download_button(
                        label="📥 Télécharger CSV",
                        data=csv_data,
                        file_name=f"todos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
            else:
                json_data = export_todos_json()
                st.download_button(
                    label="📥 Télécharger JSON",
                    data=json_data,
                    file_name=f"todos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    use_container_width=True
                )
        
        with col2:
            st.markdown("#### 🧹 Maintenance")
            
            todos = load_todos()
            completed_count = sum(1 for t in todos if t["completed"])
            
            if completed_count > 0:
                if st.button(f"🗑️ Supprimer {completed_count} tâches complétées", use_container_width=True):
                    todos = [t for t in todos if not t["completed"]]
                    save_todos(todos)
                    st.success(f"✅ {completed_count} tâches supprimées!")
                    st.rerun()
        
        st.markdown("---")
        
        # Database info
        st.markdown("#### 💾 Informations de base de données")
        
        todos = load_todos()
        stats = get_statistics()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Fichier de données", "todos.json")
        
        with col2:
            file_size = os.path.getsize(DATA_FILE) if os.path.exists(DATA_FILE) else 0
            st.metric("Taille du fichier", f"{file_size / 1024:.2f} KB")
        
        with col3:
            st.metric("Localisation", "Dossier courant")
        
        st.markdown("---")
        
        # Danger zone
        st.markdown("#### ⚠️ Zone dangereuse")
        
        if st.checkbox("Je comprends que cette action est irréversible"):
            if st.button("🔴 SUPPRIMER TOUTES LES TÂCHES", use_container_width=True):
                save_todos([])
                st.warning("❌ Toutes les tâches ont été supprimées!")
                st.rerun()

if __name__ == "__main__":
    main()
