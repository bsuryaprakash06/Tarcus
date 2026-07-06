import os

for root, _, files in os.walk('src/tools'):
    for f in files:
        if f.endswith('.py'):
            path = os.path.join(root, f)
            with open(path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # The exact string is user_message="f"Simulating attempt to terminate process matching '{app_name}'."",
            content = content.replace('user_message="f"', 'user_message=f"')
            content = content.replace('\'"",', '\'",')
            content = content.replace('."",', '.",')
            content = content.replace('user_message=""', 'user_message="')
            content = content.replace('"".",', '".",')
            content = content.replace('."",', '.",')
            content = content.replace('"",', '",')

            with open(path, 'w', encoding='utf-8') as file:
                file.write(content)
print('Quotes fixed.')
