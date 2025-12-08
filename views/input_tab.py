from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, 
                             QLabel, QHeaderView, QGroupBox, QFormLayout, QDoubleSpinBox, 
                             QPushButton, QHBoxLayout, QAbstractItemView, QMessageBox)
from PyQt6.QtCore import Qt

class InputTab(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
        # Internal storage for relationships
        # map segment_row -> {plan_id: {'a': ..., 'b': ...}}
        self.demand_data = {} 

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # 1. Capacity Input
        cap_group = QGroupBox("Network Constraints")
        cap_layout = QFormLayout(cap_group)
        self.capacity_input = QDoubleSpinBox()
        self.capacity_input.setRange(0, 1e9)
        self.capacity_input.setSingleStep(1000)
        self.capacity_input.setValue(100000)
        self.capacity_input.setSuffix(" GB")
        cap_layout.addRow("Total Network Capacity:", self.capacity_input)
        layout.addWidget(cap_group)

        # 2. Plans Table (Editable)
        plans_group = QGroupBox("Telecom Plans")
        p_layout = QVBoxLayout(plans_group)
        
        # Tools for Plans
        p_tools = QHBoxLayout()
        btn_add_plan = QPushButton("Add Plan")
        btn_add_plan.clicked.connect(self.add_plan_row)
        btn_del_plan = QPushButton("Remove Plan")
        btn_del_plan.clicked.connect(self.remove_plan_row)
        p_tools.addWidget(btn_add_plan)
        p_tools.addWidget(btn_del_plan)
        p_tools.addStretch()
        p_layout.addLayout(p_tools)

        self.plans_table = QTableWidget()
        self.plans_table.setColumnCount(4)
        self.plans_table.setHorizontalHeaderLabels(["ID", "Name", "Data (GB)", "Cost ($)"])
        self.plans_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.plans_table.itemChanged.connect(self.on_plan_changed)
        p_layout.addWidget(self.plans_table)
        layout.addWidget(plans_group)

        # 3. Segments Table & Demand Params
        seg_group = QGroupBox("Customer Segments & Demand")
        s_main_layout = QVBoxLayout(seg_group)
        
        # Tools for Segments
        s_tools = QHBoxLayout()
        btn_add_seg = QPushButton("Add Segment")
        btn_add_seg.clicked.connect(self.add_segment_row)
        btn_del_seg = QPushButton("Remove Segment")
        btn_del_seg.clicked.connect(self.remove_segment_row)
        s_tools.addWidget(btn_add_seg)
        s_tools.addWidget(btn_del_seg)
        s_tools.addStretch()
        s_main_layout.addLayout(s_tools)

        # HBox for Segments List vs Demand Params
        s_content = QHBoxLayout()
        
        # Left: Segments List
        self.segments_table = QTableWidget()
        self.segments_table.setColumnCount(3)
        self.segments_table.setHorizontalHeaderLabels(["ID", "Name", "Population"])
        self.segments_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.segments_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.segments_table.itemSelectionChanged.connect(self.load_demand_params)
        s_content.addWidget(self.segments_table, 1) # Stretch factor 1

        # Right: Demand Params for Selected Segment
        demand_layout = QVBoxLayout()
        self.lbl_demand = QLabel("Select a segment to edit demand parameters")
        demand_layout.addWidget(self.lbl_demand)
        
        self.demand_table = QTableWidget()
        self.demand_table.setColumnCount(3)
        self.demand_table.setHorizontalHeaderLabels(["Plan ID", "Intercept (a)", "Slope (b)"])
        self.demand_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.demand_table.itemChanged.connect(self.save_demand_params) # Auto-save when edited
        demand_layout.addWidget(self.demand_table)
        
        s_content.addLayout(demand_layout, 1) # Stretch factor 1
        
        s_main_layout.addLayout(s_content)
        layout.addWidget(seg_group)

    # --- Data Loading ---
    
    def load_data(self, plans, segments, capacity):
        """Populate tables with data."""
        self.capacity_input.setValue(capacity)

        # Populate Plans
        self.plans_table.blockSignals(True)
        self.plans_table.setRowCount(0)
        for p in plans:
            self.add_plan_row(p)
        self.plans_table.blockSignals(False)

        # Populate Segments
        self.segments_table.blockSignals(True)
        self.segments_table.setRowCount(0)
        self.demand_data = {} # Clear old
        
        for s in segments:
            row = self.segments_table.rowCount()
            self.segments_table.insertRow(row)
            self.segments_table.setItem(row, 0, QTableWidgetItem(str(s['id'])))
            self.segments_table.setItem(row, 1, QTableWidgetItem(str(s['name'])))
            self.segments_table.setItem(row, 2, QTableWidgetItem(str(s['size'])))
            
            # Store demand params
            self.demand_data[row] = s['params'] # {PlanID: {a:.., b:..}}

        self.segments_table.blockSignals(False)
        
    # --- Plans Actions ---

    def add_plan_row(self, data=None):
        row = self.plans_table.rowCount()
        self.plans_table.insertRow(row)
        if data:
            self.plans_table.setItem(row, 0, QTableWidgetItem(str(data['id'])))
            self.plans_table.setItem(row, 1, QTableWidgetItem(str(data['name'])))
            self.plans_table.setItem(row, 2, QTableWidgetItem(str(data['data_limit'])))
            self.plans_table.setItem(row, 3, QTableWidgetItem(str(data['cost'])))
        else:
            # Default new plan
            self.plans_table.setItem(row, 0, QTableWidgetItem(f"P{row+1}"))
            self.plans_table.setItem(row, 1, QTableWidgetItem("New Plan"))
            self.plans_table.setItem(row, 2, QTableWidgetItem("10.0"))
            self.plans_table.setItem(row, 3, QTableWidgetItem("5.0"))
            
    def remove_plan_row(self):
        cur = self.plans_table.currentRow()
        if cur >= 0:
            self.plans_table.removeRow(cur)

    def on_plan_changed(self, item):
        # Trigger redraw of demand table if Plan ID changed, but for now just optional
        pass

    # --- Segments Actions ---

    def add_segment_row(self):
        row = self.segments_table.rowCount()
        self.segments_table.insertRow(row)
        self.segments_table.setItem(row, 0, QTableWidgetItem(f"S{row+1}"))
        self.segments_table.setItem(row, 1, QTableWidgetItem("New Segment"))
        self.segments_table.setItem(row, 2, QTableWidgetItem("1000"))
        self.demand_data[row] = {} # Init empty params

    def remove_segment_row(self):
        cur = self.segments_table.currentRow()
        if cur >= 0:
            self.segments_table.removeRow(cur)
            if cur in self.demand_data:
                del self.demand_data[cur]
                # Re-index keys > cur? Yes, this is tricky with dict.
                # Better to map IDs, but row index is easier for UI if strict.
                # Re-build dict:
                new_data = {}
                for r in range(self.segments_table.rowCount()):
                    old_r = r if r < cur else r + 1
                    if old_r in self.demand_data:
                        new_data[r] = self.demand_data[old_r]
                self.demand_data = new_data
                self.load_demand_params() # Refresh

    def load_demand_params(self):
        """Show demand params for selected segment."""
        row = self.segments_table.currentRow()
        if row < 0:
            self.lbl_demand.setText("Select a segment...")
            self.demand_table.setRowCount(0)
            return
            
        seg_name = self.segments_table.item(row, 1).text()
        self.lbl_demand.setText(f"Demand for: {seg_name}")
        
        current_params = self.demand_data.get(row, {}) # {PlanID: {a:.., b:..}}
        
        # Rows = Plans
        self.demand_table.blockSignals(True)
        self.demand_table.setRowCount(self.plans_table.rowCount())
        for r in range(self.plans_table.rowCount()):
            # Get Plan ID
            p_item = self.plans_table.item(r, 0)
            pid = p_item.text() if p_item else ""
            
            self.demand_table.setItem(r, 0, QTableWidgetItem(pid))
            # Parameters
            params = current_params.get(pid, {'a': 0, 'b': 0})
            self.demand_table.setItem(r, 1, QTableWidgetItem(str(params['a'])))
            self.demand_table.setItem(r, 2, QTableWidgetItem(str(params['b'])))
            
            # Make Plan ID read-only in this view
            self.demand_table.item(r, 0).setFlags(Qt.ItemFlag.ItemIsEnabled)
            
        self.demand_table.blockSignals(False)

    def save_demand_params(self, item):
        """Save edited 'a' or 'b' back to storage."""
        seg_row = self.segments_table.currentRow()
        if seg_row < 0: 
            return
            
        row = item.row()
        col = item.column()
        
        # row corresponds to Plan row in plans_table
        pid_item = self.demand_table.item(row, 0)
        pid = pid_item.text()
        
        if seg_row not in self.demand_data:
            self.demand_data[seg_row] = {}
        if pid not in self.demand_data[seg_row]:
            self.demand_data[seg_row][pid] = {'a': 0, 'b': 0}
            
        try:
            val = float(item.text())
        except ValueError:
            val = 0.0
            
        if col == 1: # a
            self.demand_data[seg_row][pid]['a'] = val
        elif col == 2: # b
            self.demand_data[seg_row][pid]['b'] = val

    # --- Data Extraction ---

    def get_data(self):
        """Scrape all tables and return structured data."""
        # 1. Plans
        plans = []
        for r in range(self.plans_table.rowCount()):
            try:
                plans.append({
                    'id': self.plans_table.item(r, 0).text(),
                    'name': self.plans_table.item(r, 1).text(),
                    'data_limit': float(self.plans_table.item(r, 2).text()),
                    'cost': float(self.plans_table.item(r, 3).text())
                })
            except ValueError:
                pass # Skip invalid rows

        # 2. Segments
        segments = []
        for r in range(self.segments_table.rowCount()):
            try:
                sid = self.segments_table.item(r, 0).text()
                seg = {
                    'id': sid,
                    'name': self.segments_table.item(r, 1).text(),
                    'size': float(self.segments_table.item(r, 2).text()),
                    'params': self.demand_data.get(r, {})
                }
                # Ensure params match current plans
                # The user might have added a plan but haven't clicked the segment to init params.
                # So we iterate plans and ensure they exist
                for p in plans:
                    pid = p['id']
                    if pid not in seg['params']:
                        seg['params'][pid] = {'a': 0, 'b': 0} # Default
                
                segments.append(seg)
            except ValueError:
                pass

        capacity = self.capacity_input.value()
        return plans, segments, capacity

    def get_capacity(self):
        return self.capacity_input.value()
