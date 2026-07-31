from lca.agent import LuxuryConciergeAgent


def test_agent_recommends_spectre_for_electric_client():
    agent = LuxuryConciergeAgent()
    result = agent.invoke("London client wants a quiet electric car with sustainable materials.")
    assert result["configuration"]["model"] == "Spectre"
    assert "Estimated investment" in result["response"]


def test_agent_uses_memory_for_region():
    agent = LuxuryConciergeAgent()
    memory = [{"role": "user", "content": "The client is based in Dubai."}]
    result = agent.invoke("They want a family car for mountain trips.", memory=memory)
    assert result["region"] == "GCC"
    assert result["configuration"]["model"] == "Cullinan"


def test_region_cues_match_on_word_boundaries():
    """"usage" contains "usa" - substring matching sent GCC clients to the US."""
    agent = LuxuryConciergeAgent()
    result = agent.invoke("Dubai client, mountain usage, 10-month timeline.")
    assert result["region"] == "GCC"


def test_assistant_turns_do_not_pollute_the_client_profile():
    agent = LuxuryConciergeAgent()
    memory = [
        {
            "role": "assistant",
            "content": "Describe the client, region, usage, cabin mood, timeline, and budget.",
        }
    ]
    result = agent.invoke("Dubai client wants a family car for mountain trips.", memory=memory)
    assert "Describe the client" not in result["client_profile"]
    assert result["region"] == "GCC"

