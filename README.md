# todo.txt as a Telegram bot
A bot to hold your todo.txt tasks

## setup and installation

### install
1. `git clone` the project or download it
2. Create bot with [@botfather](https://t.me/botfather)
3. create `YOUR_CONFIG_DIRECTORY/config.json`:
   ```json
   {
       "token": "YOUR_BOT_TOKEN"
   }
   ```
4. run `cp docker-compose.example docker-compose.yml` 
5. run `mkdir YOUR_CONFIG_DIRECTORY` 
6. run `echo {} > YOUR_CONFIG_DIRECTORY/tasks.json` 
7. edit `docker-compose.yml` bot.volumes to match your directory with your tasks
8. run `docker-compose up`

## commands
See [help.md](help.md)
