import os
import json
from typing import List, Union

from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.schema import SystemMessage, HumanMessage, AIMessage
from langchain_community.chat_message_histories import ChatMessageHistory


class ChatHistoryManager:

    def __init__(self, file_path: str):
        self.file_path = file_path

    def load(self) -> List[Union[HumanMessage, AIMessage]]:
        """Загружает историю чата из файла"""
        if os.path.exists(self.file_path):
            with open(self.file_path, "r", encoding="utf-8") as file:
                try:
                    data = json.load(file)
                    return [HumanMessage(content=m["human"]) if "human" in m 
                           else AIMessage(content=m["ai"]) for m in data]
                except json.JSONDecodeError:
                    return []
        return []

    def save(self, messages: List[Union[HumanMessage, AIMessage]]) -> None:
        """Сохраняет историю чата в файл"""
        with open(self.file_path, "w", encoding="utf-8") as file:
            json.dump([{"human": msg.content} if isinstance(msg, HumanMessage) 
                      else {"ai": msg.content} for msg in messages], 
                     file, ensure_ascii=False, indent=2)


class ChatBot:

    def __init__(self, api_key: str, history_file: str, prompt_file: str):
        """Инициализация чат-бота"""
        self.history_manager = ChatHistoryManager(history_file)
        self.llm = ChatOpenAI(
            model_name="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
            openai_api_key=api_key,
            openai_api_base="https://api.together.xyz/v1"
        )
        self.system_message = self.read_file_txt(prompt_file)  # Загружаем промпт из файла
        self.memory = self._initialize_memory()

    def read_file_txt(self, file_path: str) -> str:
        """Чтение текста из файла"""
        try:
            with open(file_path, "r", encoding='utf-8') as file:
                content = file.read()
            return content
        except FileNotFoundError:
            return "Промпт не найден, продолжим без него."
        
    def _initialize_memory(self) -> ConversationBufferMemory:
        """Инициализация памяти с историей чата"""
        chat_history = ChatMessageHistory(messages=self.history_manager.load())
        return ConversationBufferMemory(chat_memory=chat_history, return_messages=True)

    def process_input(self, user_input: str) -> str:
        """Обработка пользовательского ввода и генерация ответа"""
        try:
            # Добавляем системное сообщение и сообщение пользователя в память
            if not any(isinstance(msg, SystemMessage) for msg in self.memory.chat_memory.messages):
                self.memory.chat_memory.add_message(SystemMessage(content=self.system_message))
            self.memory.chat_memory.add_message(HumanMessage(content=user_input))

            # Получаем ответ от модели
            response = self.llm.invoke(self.memory.chat_memory.messages)
            self.memory.chat_memory.add_message(AIMessage(content=response.content))

            # Сохраняем историю
            self.history_manager.save(self.memory.chat_memory.messages)
            return response.content

        except Exception as e:
            return f"Ошибка: {str(e)}"

    def run(self, user_input: str) -> Union[str, dict]:
        """Запуск основного цикла чата"""
        try:
            response = self.process_input(user_input).replace('*', '')

            # Удаляем лишние символы и экранированные символы
            response = response.replace("\\n", "").replace("\\t", "")  # Убираем символы новой строки и табуляции
            response = response.replace("\'", "\"")  # Убираем экранированные одинарные кавычки
            response = response.replace("None", "null")  # Заменяем None на null для корректного JSON

            # Преобразуем строку в валидный JSON
            try:
                response_json = json.loads(response)
                return response_json
            except json.JSONDecodeError:
                # Если не JSON, просто возвращаем строку
                return response

        except KeyboardInterrupt:
            print("\nВы принудительно остановили диалог 🛑")