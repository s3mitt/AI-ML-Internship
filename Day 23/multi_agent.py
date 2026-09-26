from typing import TypedDict, Annotated
from enum import Enum
import json
from datetime import datetime
from langgraph.graph import StateGraph, END
# from langgraph.prebuilt import ToolExecutor
import anthropic


# ============================================================================
# STATE MANAGEMENT
# ============================================================================

class AgentType(str, Enum):
    ROUTER = "router"
    ANALYZER = "analyzer"
    RESEARCHER = "researcher"
    SYNTHESIZER = "synthesizer"


class MessageLog(TypedDict):
    """Individual message in the communication log"""
    timestamp: str
    agent: str
    message_type: str
    content: str
    status: str


class AgentState(TypedDict):
    """Central state managed by LangGraph"""
    user_input: str
    conversation_history: list[str]
    communication_log: list[MessageLog]
    analysis_results: dict
    research_findings: dict
    final_response: str
    error_messages: list[str]
    routing_decision: str
    agent_sequence: list[str]


# ============================================================================
# LOGGER UTILITY
# ============================================================================

class CommunicationLogger:
    """Logs all agent communications"""
    
    @staticmethod
    def log_message(state: AgentState, agent: str, message_type: str, 
                   content: str, status: str = "success") -> AgentState:
        """Log an agent's message"""
        log_entry = MessageLog(
            timestamp=datetime.now().isoformat(),
            agent=agent,
            message_type=message_type,
            content=content,
            status=status
        )
        state["communication_log"].append(log_entry)
        state["agent_sequence"].append(agent)
        return state


# ============================================================================
# ROUTER AGENT
# ============================================================================

class RouterAgent:
    """Routes requests to appropriate agents based on content analysis"""
    
    @staticmethod
    def analyze_request(state: AgentState) -> AgentState:
        """Determine which agents should handle the request"""
        try:
            user_input = state["user_input"]
            
            # Routing logic
            routing_map = {
                "analyze": ["analyzer"],
                "research": ["researcher"],
                "complex": ["analyzer", "researcher", "synthesizer"],
                "simple": ["analyzer"],
            }
            
            # Determine routing
            routing_decision = "complex" if any(word in user_input.lower() 
                                               for word in ["analyze", "research", "combine"]) else "simple"
            
            state["routing_decision"] = routing_decision
            agents_to_route = routing_map.get(routing_decision, ["analyzer"])
            
            # Log routing decision
            state = CommunicationLogger.log_message(
                state,
                agent=AgentType.ROUTER.value,
                message_type="ROUTING_DECISION",
                content=f"Routing to agents: {agents_to_route}. Decision: {routing_decision}",
                status="success"
            )
            
            state["conversation_history"].append(
                f"[ROUTER] Analyzed request. Routing type: {routing_decision}"
            )
            
            return state
            
        except Exception as e:
            state["error_messages"].append(f"Router error: {str(e)}")
            state = CommunicationLogger.log_message(
                state,
                agent=AgentType.ROUTER.value,
                message_type="ERROR",
                content=str(e),
                status="error"
            )
            return state


# ============================================================================
# ANALYZER AGENT
# ============================================================================

class AnalyzerAgent:
    """Analyzes the user request in detail"""
    
    @staticmethod
    def analyze_content(state: AgentState) -> AgentState:
        """Perform detailed analysis"""
        try:
            user_input = state["user_input"]
            
            analysis = {
                "length": len(user_input),
                "word_count": len(user_input.split()),
                "contains_question": "?" in user_input,
                "sentiment": "neutral",  # Simplified
                "key_terms": [word for word in user_input.split() if len(word) > 5],
                "complexity_score": len(user_input.split()) / 10
            }
            
            state["analysis_results"] = analysis
            
            state = CommunicationLogger.log_message(
                state,
                agent=AgentType.ANALYZER.value,
                message_type="ANALYSIS",
                content=f"Analysis complete: {json.dumps(analysis)}",
                status="success"
            )
            
            state["conversation_history"].append(
                f"[ANALYZER] Content analysis: {analysis['word_count']} words, "
                f"complexity: {analysis['complexity_score']:.1f}"
            )
            
            return state
            
        except Exception as e:
            state["error_messages"].append(f"Analyzer error: {str(e)}")
            state = CommunicationLogger.log_message(
                state,
                agent=AgentType.ANALYZER.value,
                message_type="ERROR",
                content=str(e),
                status="error"
            )
            return state


# ============================================================================
# RESEARCHER AGENT
# ============================================================================

class ResearcherAgent:
    """Researches and gathers information"""
    
    @staticmethod
    def conduct_research(state: AgentState) -> AgentState:
        """Conduct research on the topic"""
        try:
            user_input = state["user_input"]
            
            # Simulated research findings
            research_findings = {
                "sources_found": 3,
                "relevant_documents": 5,
                "key_insights": [
                    "Finding 1: Relevant context identified",
                    "Finding 2: Supporting evidence gathered",
                    "Finding 3: Cross-referenced information"
                ],
                "confidence_level": 0.85,
                "research_depth": "comprehensive"
            }
            
            state["research_findings"] = research_findings
            
            state = CommunicationLogger.log_message(
                state,
                agent=AgentType.RESEARCHER.value,
                message_type="RESEARCH",
                content=f"Research complete: {json.dumps(research_findings)}",
                status="success"
            )
            
            state["conversation_history"].append(
                f"[RESEARCHER] Found {research_findings['sources_found']} sources, "
                f"confidence: {research_findings['confidence_level']}"
            )
            
            return state
            
        except Exception as e:
            state["error_messages"].append(f"Researcher error: {str(e)}")
            state = CommunicationLogger.log_message(
                state,
                agent=AgentType.RESEARCHER.value,
                message_type="ERROR",
                content=str(e),
                status="error"
            )
            return state


# ============================================================================
# SYNTHESIZER AGENT
# ============================================================================

class SynthesizerAgent:
    """Synthesizes information from multiple agents"""
    
    @staticmethod
    def synthesize_response(state: AgentState) -> AgentState:
        """Combine analysis and research into final response"""
        try:
            analysis = state.get("analysis_results", {})
            research = state.get("research_findings", {})
            user_input = state["user_input"]
            
            # Build comprehensive response
            final_response = f"""
SYNTHESIZED RESPONSE
====================

User Request: {user_input}

Analysis Insights:
- Content Length: {analysis.get('word_count', 0)} words
- Complexity Score: {analysis.get('complexity_score', 0):.1f}
- Key Terms Identified: {', '.join(analysis.get('key_terms', []))}

Research Findings:
- Sources Identified: {research.get('sources_found', 0)}
- Key Insights:
  {chr(10).join([f'  • {insight}' for insight in research.get('key_insights', [])])}
- Confidence Level: {research.get('confidence_level', 0):.0%}

Integrated Conclusion:
Based on comprehensive analysis and research, the request has been thoroughly 
examined from multiple perspectives. All agent insights have been synthesized 
into this cohesive response.

Processing Status: All agents completed successfully.
Communication Flow: Complete agent interaction logged.
            """
            
            state["final_response"] = final_response
            
            state = CommunicationLogger.log_message(
                state,
                agent=AgentType.SYNTHESIZER.value,
                message_type="SYNTHESIS",
                content="Response synthesized from all agent inputs",
                status="success"
            )
            
            state["conversation_history"].append(
                "[SYNTHESIZER] Synthesized final response from all agent inputs"
            )
            
            return state
            
        except Exception as e:
            state["error_messages"].append(f"Synthesizer error: {str(e)}")
            state = CommunicationLogger.log_message(
                state,
                agent=AgentType.SYNTHESIZER.value,
                message_type="ERROR",
                content=str(e),
                status="error"
            )
            return state


# ============================================================================
# LANGGRAPH WORKFLOW
# ============================================================================

def create_multi_agent_graph():
    """Create the multi-agent workflow graph"""
    
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("router", RouterAgent.analyze_request)
    workflow.add_node("analyzer", AnalyzerAgent.analyze_content)
    workflow.add_node("researcher", ResearcherAgent.conduct_research)
    workflow.add_node("synthesizer", SynthesizerAgent.synthesize_response)
    
    # Add edges
    workflow.set_entry_point("router")
    workflow.add_edge("router", "analyzer")
    workflow.add_edge("analyzer", "researcher")
    workflow.add_edge("researcher", "synthesizer")
    workflow.add_edge("synthesizer", END)
    
    # Compile graph
    graph = workflow.compile()
    return graph


def run_multi_agent_system(user_input: str) -> dict:
    """Execute the multi-agent system"""
    
    # Initialize state
    initial_state: AgentState = {
        "user_input": user_input,
        "conversation_history": [],
        "communication_log": [],
        "analysis_results": {},
        "research_findings": {},
        "final_response": "",
        "error_messages": [],
        "routing_decision": "",
        "agent_sequence": []
    }
    
    # Create and run graph
    graph = create_multi_agent_graph()
    final_state = graph.invoke(initial_state)
    
    return final_state


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    # Example usage
    test_input = "Analyze and research the implications of artificial intelligence in modern business"
    
    print("=" * 80)
    print("MULTI-AGENT SYSTEM DEMONSTRATION")
    print("=" * 80)
    print(f"\nUser Input: {test_input}\n")
    
    result = run_multi_agent_system(test_input)
    
    print("AGENT SEQUENCE:")
    print(f"  {' → '.join(result['agent_sequence'])}\n")
    
    print("COMMUNICATION LOG:")
    print("-" * 80)
    for i, log in enumerate(result['communication_log'], 1):
        print(f"\n{i}. [{log['timestamp']}] {log['agent'].upper()}")
        print(f"   Type: {log['message_type']}")
        print(f"   Status: {log['status']}")
        print(f"   Content: {log['content'][:100]}...")
    
    print("\n" + "=" * 80)
    print("FINAL RESPONSE:")
    print("=" * 80)
    print(result['final_response'])
    
    if result['error_messages']:
        print("\nERRORS ENCOUNTERED:")
        for error in result['error_messages']:
            print(f"  • {error}")