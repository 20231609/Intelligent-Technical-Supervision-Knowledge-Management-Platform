import { CheckCircleFilled, DownOutlined } from "@ant-design/icons";

import type { ThinkingStep } from "@/types/chat";

import "./ThinkingSteps.css";

interface ThinkingStepsProps {
  steps: ThinkingStep[];
  expanded: boolean;
  onToggle: () => void;
  isStreaming: boolean;
}

function getStepIcon(step: ThinkingStep): string {
  if (step.icon) {
    return step.icon;
  }
  if (step.status === "running") {
    return "...";
  }
  if (step.status === "failed") {
    return "!";
  }
  return "OK";
}

function isThinkingComplete(steps: ThinkingStep[], isStreaming: boolean): boolean {
  if (steps.length === 0) {
    return false;
  }

  const lastStep = steps[steps.length - 1];
  if (lastStep.id === "generate-done" && lastStep.status === "done") {
    return true;
  }

  return !isStreaming && steps.every((step) => step.status === "done");
}

const ThinkingSteps = ({ steps, expanded, onToggle, isStreaming }: ThinkingStepsProps) => {
  if (steps.length === 0) {
    return null;
  }

  const thinkingComplete = isThinkingComplete(steps, isStreaming);
  const headerTitle = thinkingComplete ? "已完成思考" : "思考过程";

  return (
    <div className="thinking-steps-panel">
      <button type="button" className="thinking-steps-panel__header" onClick={onToggle}>
        <span className="thinking-steps-panel__title">{headerTitle}</span>
        <DownOutlined
          className={`thinking-steps-panel__chevron ${
            expanded ? "thinking-steps-panel__chevron--expanded" : ""
          }`}
        />
      </button>

      {expanded ? (
        <div className="thinking-steps-panel__body">
          <ul className="thinking-steps-panel__list">
            {steps.map((step, index) => (
              <li
                key={`${step.id}-${index}`}
                className={`thinking-steps-panel__item thinking-steps-panel__item--${step.status}`}
              >
                <span className="thinking-steps-panel__emoji" aria-hidden>
                  {getStepIcon(step)}
                </span>
                <span className="thinking-steps-panel__label">{step.label}</span>
              </li>
            ))}
          </ul>

          {thinkingComplete ? (
            <div className="thinking-steps-panel__footer">
              <CheckCircleFilled className="thinking-steps-panel__footer-icon" />
              <span>已完成</span>
            </div>
          ) : null}
        </div>
      ) : null}
    </div>
  );
};

export default ThinkingSteps;
