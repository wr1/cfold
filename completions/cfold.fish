# Fish shell completions for cfold CLI

# Main cfold command
complete -c cfold -f -n '__fish_use_subcommand' -a fold -d 'Fold files or directory into a single text file'
complete -c cfold -f -n '__fish_use_subcommand' -a unfold -d 'Unfold a modified fold file into a directory'
complete -c cfold -f -n '__fish_use_subcommand' -a init -d 'Initialize a project template with LLM instructions'

# Fold subcommand options
complete -c cfold -f -n '__fish_seen_subcommand_from fold' -l output -s o -d 'Output file' -r
complete -c cfold -f -n '__fish_seen_subcommand_from fold' -l prompt -s p -d 'Prompt file to append' -r
complete -c cfold -f -n '__fish_seen_subcommand_from fold' -l dialect -s d -d 'Instruction dialect' -r
complete -c cfold -f -n '__fish_seen_subcommand_from fold' -a '(__fish_complete_path)' -d 'Files or directories to fold'

# Unfold subcommand options
complete -c cfold -f -n '__fish_seen_subcommand_from unfold' -l original-dir -s i -d 'Original project directory' -r
complete -c cfold -f -n '__fish_seen_subcommand_from unfold' -l output-dir -s o -d 'Output directory' -r
complete -c cfold -f -n '__fish_seen_subcommand_from unfold' -a '(__fish_complete_path)' -d 'Fold file to unfold'

# Init subcommand options
complete -c cfold -f -n '__fish_seen_subcommand_from init' -l custom -s c -d 'Custom instruction' -r
complete -c cfold -f -n '__fish_seen_subcommand_from init' -l dialect -s d -d 'Instruction dialect' -r
complete -c cfold -f -n '__fish_seen_subcommand_from init' -a '(__fish_complete_path)' -d 'Output file'
