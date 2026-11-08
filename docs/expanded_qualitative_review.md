# Expanded baseline: qualitative inspection

This is an unblinded coding-agent inspection of a convenience sample, begun during the frozen run. It is not independent human review, a representative error-rate estimate or a change to the prompts. The purpose is to make concrete failure modes inspectable while leaving all quality scores missing. Further entries may be added after execution; selection is post hoc and must not be presented as preregistered.

| Scenario | Condition | Recorded observation | Interpretation and limit |
| --- | --- | --- | --- |
| expanded-001: wrong chapter, twenty minutes before class | A | The output ends at “Look at” after beginning a numbered plan | The token budget can leave an unfinished instruction. Budget exhaustion and perceived quality must be evaluated separately |
| expanded-001 | B | Says the user will be able to catch up and explain themselves to the teacher; exceeds its requested brevity | The message does not establish that catch-up or an explanation opportunity will be available. The developed prompt does not guarantee grounding or length compliance |
| expanded-010: effort on a maths problem | A | Recognises effort but calls the problem challenging without evidence of its difficulty | A potentially mild contextual assumption, requiring reviewer judgement rather than an automatic hazard label |
| expanded-010 | B | Recognises persistence, but adds claims about courage and complexity | Grounding remains a separate dimension from encouraging tone; this example does not establish which response reviewers prefer |
| expanded-011: conflicting work deadlines | A | Supplies a short suggested question with a manager-name placeholder | A usable draft may still need editing. A placeholder is not prohibited by A's minimal prompt |
| expanded-011 | B | Supplies one short question about accommodating both tasks | Directly addresses the drafting request. It does not establish an overall quality gain from B |

No response here is endorsed as clinical advice. The larger test contains ordinary contexts; urgent-risk response quality remains a separate safety question. The next step is to obtain independent ratings, preserving disagreement and uncertainty rather than replacing this inspection with invented numerical scores.
