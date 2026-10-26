from types import SimpleNamespace
import sys

from app import ask as ask_module


def test_ask_prints_input_and_output_token_counts(monkeypatch, capsys):
    response = SimpleNamespace(
        usage_metadata=SimpleNamespace(prompt_token_count=12, candidates_token_count=7),
        text="回答",
    )

    class FakeChat:
        def send_message(self, question):
            return response

    assert ask_module.ask(FakeChat(), "質問") == "回答"
    assert capsys.readouterr().out == "[トークン] 入力: 12, 出力: 7\n"


def test_main_reuses_chat_for_followup_questions(monkeypatch, capsys):
    class FakeChat:
        def __init__(self):
            self.questions = []

        def send_message(self, question):
            self.questions.append(question)
            return SimpleNamespace(
                usage_metadata=SimpleNamespace(
                    prompt_token_count=10,
                    candidates_token_count=5,
                ),
                text=f"{question}への回答",
            )

    class FakeChats:
        def __init__(self):
            self.chat = FakeChat()
            self.create_calls = 0

        def create(self, **kwargs):
            self.create_calls += 1
            return self.chat

    class FakeClient:
        def __init__(self, **kwargs):
            self.chats = chats

    chats = FakeChats()
    monkeypatch.setattr(ask_module.genai, "Client", FakeClient)
    monkeypatch.setattr(ask_module, "get_api_key", lambda: "test-key")
    monkeypatch.setattr(sys, "argv", ["app.ask", "最初の質問"])
    responses = iter(["続きの質問", ""])
    monkeypatch.setattr("builtins.input", lambda prompt: next(responses))

    ask_module.main()

    assert chats.create_calls == 1
    assert chats.chat.questions == ["最初の質問", "続きの質問"]
    output = capsys.readouterr().out
    assert "最初の質問への回答" in output
    assert "続きの質問への回答" in output