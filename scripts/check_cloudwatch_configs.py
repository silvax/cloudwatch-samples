import json
import sys
from typing import List, Dict

def load_json_file(file_path: str) -> Dict:
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        print(f"Error: {file_path} is not a valid JSON file")
        sys.exit(1)
    except FileNotFoundError:
        print(f"Error: File {file_path} not found")
        sys.exit(1)

def get_metrics_section(config: Dict) -> Dict:
    return config.get('metrics', {}).get('metrics_collected', {})

def get_logs_section(config: Dict) -> Dict:
    return config.get('logs', {}).get('logs_collected', {})

def compare_metrics_configs(files: List[str]) -> bool:
    has_conflicts = False
    configs = []
    
    for file in files:
        config = load_json_file(file)
        metrics_config = get_metrics_section(config)
        if metrics_config:
            configs.append((file, metrics_config))
    
    if len(configs) <= 1:
        return True

    # List of metrics that must be identical across files
    strict_metrics = ['cpu', 'disk', 'diskio', 'mem', 'net', 'netstat', 'swap']
    
    base_file, base_config = configs[0]
    for file, config in configs[1:]:
        for metric in strict_metrics:
            base_metric = base_config.get(metric, {})
            current_metric = config.get(metric, {})
            
            if base_metric and current_metric and base_metric != current_metric:
                print(f"\nConflict detected in {metric} configuration:")
                print(f"File: {base_file} has config:")
                print(json.dumps(base_metric, indent=2))
                print(f"File: {file} has different config:")
                print(json.dumps(current_metric, indent=2))
                has_conflicts = True

        # Check for custom metrics conflicts
        base_custom = base_config.get('custom_metrics', [])
        current_custom = config.get('custom_metrics', [])
        
        if base_custom and current_custom:
            for metric in base_custom:
                if metric in current_custom and base_custom[metric] != current_custom[metric]:
                    print(f"\nConflict detected in custom metric {metric}:")
                    print(f"File: {base_file} has config:")
                    print(json.dumps(base_custom[metric], indent=2))
                    print(f"File: {file} has different config:")
                    print(json.dumps(current_custom[metric], indent=2))
                    has_conflicts = True

    return not has_conflicts

def compare_logs_configs(files: List[str]) -> bool:
    has_conflicts = False
    configs = []
    
    for file in files:
        config = load_json_file(file)
        logs_config = get_logs_section(config)
        if logs_config:
            configs.append((file, logs_config))
    
    if len(configs) <= 1:
        return True

    base_file, base_config = configs[0]
    for file, config in configs[1:]:
        # Check files configurations
        base_files = base_config.get('files', {})
        current_files = config.get('files', {})
        
        if base_files and current_files:
            for log_file in base_files:
                if log_file in current_files and base_files[log_file] != current_files[log_file]:
                    print(f"\nConflict detected in log file configuration for {log_file}:")
                    print(f"File: {base_file} has config:")
                    print(json.dumps(base_files[log_file], indent=2))
                    print(f"File: {file} has different config:")
                    print(json.dumps(current_files[log_file], indent=2))
                    has_conflicts = True

        # Check Windows events configurations
        base_windows = base_config.get('windows_events', {})
        current_windows = config.get('windows_events', {})
        
        if base_windows and current_windows and base_windows != current_windows:
            print("\nConflict detected in Windows events configuration:")
            print(f"File: {base_file} has config:")
            print(json.dumps(base_windows, indent=2))
            print(f"File: {file} has different config:")
            print(json.dumps(current_windows, indent=2))
            has_conflicts = True

    return not has_conflicts

def main():
    if len(sys.argv) < 2:
        print("Usage: python script.py config1.json config2.json [config3.json ...]")
        sys.exit(1)

    files = sys.argv[1:]
    metrics_ok = compare_metrics_configs(files)
    logs_ok = compare_logs_configs(files)

    if metrics_ok and logs_ok:
        print("No configuration conflicts found")
        sys.exit(0)
    else:
        print("\nWarning: Conflicts found. Appending these configurations may fail.")
        sys.exit(1)

if __name__ == "__main__":
    main()
