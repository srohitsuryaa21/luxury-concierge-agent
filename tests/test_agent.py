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

