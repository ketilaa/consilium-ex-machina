package com.github.ketilaa.consilium.decisions.adapter;

import com.github.ketilaa.consilium.decisions.DecisionEvent;
import com.github.ketilaa.consilium.decisions.port.DecisionEventPublisher;
import java.io.PrintStream;

/** Prints every transition as it happens -- the CLI's "show your work" default adapter. */
public final class LoggingEventPublisher implements DecisionEventPublisher {

    private final PrintStream out;

    public LoggingEventPublisher() {
        this(System.out);
    }

    public LoggingEventPublisher(PrintStream out) {
        this.out = out;
    }

    @Override
    public void publish(String decisionId, DecisionEvent event) {
        out.println("  -> " + describe(event));
    }

    private static String describe(DecisionEvent event) {
        if (event instanceof DecisionEvent.Proposed) {
            return "proposed";
        } else if (event instanceof DecisionEvent.Contested e) {
            return "contested: " + e.items().size() + " item(s) raised (" + roleNames(e.items().keySet()) + ")";
        } else if (event instanceof DecisionEvent.Classified e) {
            return "classified: " + e.verdicts();
        } else if (event instanceof DecisionEvent.Revised) {
            return "revised";
        } else if (event instanceof DecisionEvent.Rechecked e) {
            return "rechecked: " + e.verdicts();
        } else if (event instanceof DecisionEvent.QuestionAnsweredExternally e) {
            return "question answered externally by " + e.role() + " (source: " + e.source() + ")";
        }
        return event.toString();
    }

    private static String roleNames(Iterable<com.github.ketilaa.consilium.decisions.Role> roles) {
        StringBuilder sb = new StringBuilder();
        for (var role : roles) {
            if (!sb.isEmpty()) {
                sb.append(", ");
            }
            sb.append(role);
        }
        return sb.toString();
    }
}
