from collections import defaultdict
from PyQt5.QtCore import Qt

class DataOperationsController:
    def __init__(self, model, undo_stack):
        self.model = model
        self.undo_stack = undo_stack
    
    def group_by_column(self, column_index, aggregate_funcs=None):
        """Группирует данные по указанному столбцу"""
        if column_index < 0 or column_index >= self.model.columnCount():
            return None
        
        groups = defaultdict(list)
        
        for row in range(self.model.rowCount()):
            key = self.model.data(self.model.index(row, column_index))
            row_data = {
                'source_row': row,
                'values': [
                    self.model.data(self.model.index(row, col))
                    for col in range(self.model.columnCount())
                ]
            }
            groups[key].append(row_data)
        
        # Применяем агрегатные функции, если они заданы
        result = []
        if aggregate_funcs:
            for key, items in groups.items():
                group_result = {'key': key, 'count': len(items)}
                for col, func in aggregate_funcs.items():
                    values = [item['values'][col] for item in items]
                    try:
                        group_result[f'col{col}_{func.__name__}'] = func(values)
                    except (TypeError, ValueError):
                        group_result[f'col{col}_{func.__name__}'] = None
                result.append(group_result)
        
        return groups if not aggregate_funcs else result
    
    @staticmethod
    def aggregate_sum(values):
        return sum(float(v) for v in values if str(v).isdigit())
    
    @staticmethod
    def aggregate_avg(values):
        nums = [float(v) for v in values if str(v).isdigit()]
        return sum(nums) / len(nums) if nums else 0
    
    @staticmethod
    def aggregate_count(values):
        return len(values)
    
    @staticmethod
    def aggregate_min(values):
        nums = [float(v) for v in values if str(v).isdigit()]
        return min(nums) if nums else None
    
    @staticmethod
    def aggregate_max(values):
        nums = [float(v) for v in values if str(v).isdigit()]
        return max(nums) if nums else None
