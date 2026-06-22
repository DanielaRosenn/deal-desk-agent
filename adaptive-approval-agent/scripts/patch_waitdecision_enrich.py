# -*- coding: utf-8 -*-
"""Patch WaitDecision.xaml email + Slack InvokeCode for enriched Salesforce fields."""
import html
from pathlib import Path

XAML = Path(
    r"c:\Users\DanielaRosenstein\OneDrive - Cato Networks\Documents\UiPath\RenewalPrice_Flow"
    r"\adaptive-approval-agent\DealDeskSolution\DealDeskApproval_WaitDecision\WaitDecision.xaml"
)
text = XAML.read_text(encoding="utf-8")

# --- Email: insert after ratSafe line ---
needle = (
    "    Dim ratSafe As String = rationale.Replace(&quot;&quot;&quot;&quot;, &quot; &quot;)"
    ".Replace(System.Environment.NewLine, &quot; &quot;)&#xA;    Dim approveBody"
)
insert = (
    "    Dim ratSafe As String = rationale.Replace(&quot;&quot;&quot;&quot;, &quot; &quot;)"
    ".Replace(System.Environment.NewLine, &quot; &quot;)&#xA;"
    "    Dim churnRisk As String = If(fd IsNot Nothing AndAlso fd(&quot;churn_risk&quot;) IsNot Nothing, "
    "fd(&quot;churn_risk&quot;).ToString(), &quot;&quot;)&#xA;"
    "    Dim custTier As String = If(fd IsNot Nothing AndAlso fd(&quot;customer_tier&quot;) IsNot Nothing, "
    "fd(&quot;customer_tier&quot;).ToString(), &quot;&quot;)&#xA;"
    "    Dim healthSc As String = If(fd IsNot Nothing AndAlso fd(&quot;health_score&quot;) IsNot Nothing, "
    "fd(&quot;health_score&quot;).ToString(), &quot;&quot;)&#xA;"
    "    Dim renewTerm As String = If(fd IsNot Nothing AndAlso fd(&quot;renewal_term_months&quot;) IsNot Nothing, "
    "fd(&quot;renewal_term_months&quot;).ToString(), &quot;&quot;)&#xA;"
    "    Dim compInv As String = If(fd IsNot Nothing AndAlso fd(&quot;competitor_involved&quot;) IsNot Nothing, "
    "fd(&quot;competitor_involved&quot;).ToString(), &quot;&quot;)&#xA;"
    "    Dim churnSafe As String = churnRisk.Replace(&quot;&quot;&quot;&quot;, &quot; &quot;)"
    ".Replace(System.Environment.NewLine, &quot; &quot;)&#xA;"
    "    Dim tierSafe As String = custTier.Replace(&quot;&quot;&quot;&quot;, &quot; &quot;)"
    ".Replace(System.Environment.NewLine, &quot; &quot;)&#xA;"
    "    Dim healthSafe As String = healthSc.Replace(&quot;&quot;&quot;&quot;, &quot; &quot;)"
    ".Replace(System.Environment.NewLine, &quot; &quot;)&#xA;"
    "    Dim termSafe As String = renewTerm.Replace(&quot;&quot;&quot;&quot;, &quot; &quot;)"
    ".Replace(System.Environment.NewLine, &quot; &quot;)&#xA;"
    "    Dim compSafe As String = compInv.Replace(&quot;&quot;&quot;&quot;, &quot; &quot;)"
    ".Replace(System.Environment.NewLine, &quot; &quot;)&#xA;    Dim approveBody"
)

if needle not in text:
    raise SystemExit("ratSafe needle not found")
text = text.replace(needle, insert, 1)

# FactSet: add 5 facts before Approval ID
old_facts = (
    "sb.AppendLine(&quot;      {&quot;&quot;title&quot;&quot;:&quot;&quot;Approver&quot;&quot;,&quot;&quot;value&quot;&quot;:&quot;&quot;&quot; &amp; approverName &amp; &quot;&quot;&quot;},&quot;)&#xA;"
    "    sb.AppendLine(&quot;      {&quot;&quot;title&quot;&quot;:&quot;&quot;Approval ID&quot;&quot;,&quot;&quot;value&quot;&quot;:&quot;&quot;&quot; &amp; approvalId &amp; &quot;&quot;&quot;}&quot;)"
)
new_facts = (
    "sb.AppendLine(&quot;      {&quot;&quot;title&quot;&quot;:&quot;&quot;Approver&quot;&quot;,&quot;&quot;value&quot;&quot;:&quot;&quot;&quot; &amp; approverName &amp; &quot;&quot;&quot;},&quot;)&#xA;"
    "    sb.AppendLine(&quot;      {&quot;&quot;title&quot;&quot;:&quot;&quot;Churn risk&quot;&quot;,&quot;&quot;value&quot;&quot;:&quot;&quot;&quot; &amp; churnSafe &amp; &quot;&quot;&quot;},&quot;)&#xA;"
    "    sb.AppendLine(&quot;      {&quot;&quot;title&quot;&quot;:&quot;&quot;Customer tier&quot;&quot;,&quot;&quot;value&quot;&quot;:&quot;&quot;&quot; &amp; tierSafe &amp; &quot;&quot;&quot;},&quot;)&#xA;"
    "    sb.AppendLine(&quot;      {&quot;&quot;title&quot;&quot;:&quot;&quot;Health score&quot;&quot;,&quot;&quot;value&quot;&quot;:&quot;&quot;&quot; &amp; healthSafe &amp; &quot;&quot;&quot;},&quot;)&#xA;"
    "    sb.AppendLine(&quot;      {&quot;&quot;title&quot;&quot;:&quot;&quot;Renewal term (mo)&quot;&quot;,&quot;&quot;value&quot;&quot;:&quot;&quot;&quot; &amp; termSafe &amp; &quot;&quot;&quot;},&quot;)&#xA;"
    "    sb.AppendLine(&quot;      {&quot;&quot;title&quot;&quot;:&quot;&quot;Competitor&quot;&quot;,&quot;&quot;value&quot;&quot;:&quot;&quot;&quot; &amp; compSafe &amp; &quot;&quot;&quot;},&quot;)&#xA;"
    "    sb.AppendLine(&quot;      {&quot;&quot;title&quot;&quot;:&quot;&quot;Approval ID&quot;&quot;,&quot;&quot;value&quot;&quot;:&quot;&quot;&quot; &amp; approvalId &amp; &quot;&quot;&quot;}&quot;)"
)
if old_facts not in text:
    raise SystemExit("FactSet block not found")
text = text.replace(old_facts, new_facts, 1)

# HTML table rows before Approval ID row
old_rows = (
    "sb.AppendLine(&quot;    &lt;tr&gt;&lt;td style=&quot;&quot;padding:6px 0;color:#64748B;font-size:13px;&quot;&quot;&gt;Approver&lt;/td&gt;"
    "&lt;td style=&quot;&quot;padding:6px 0;color:#0F172A;font-size:13px;&quot;&quot;&gt;&quot; &amp; approverName &amp; &quot;&lt;/td&gt;&lt;/tr&gt;&quot;)&#xA;"
    "    If Not String.IsNullOrWhiteSpace(requester) Then sb.AppendLine"
)
new_rows = (
    "sb.AppendLine(&quot;    &lt;tr&gt;&lt;td style=&quot;&quot;padding:6px 0;color:#64748B;font-size:13px;&quot;&quot;&gt;Approver&lt;/td&gt;"
    "&lt;td style=&quot;&quot;padding:6px 0;color:#0F172A;font-size:13px;&quot;&quot;&gt;&quot; &amp; approverName &amp; &quot;&lt;/td&gt;&lt;/tr&gt;&quot;)&#xA;"
    "    sb.AppendLine(&quot;    &lt;tr&gt;&lt;td style=&quot;&quot;padding:6px 0;color:#64748B;font-size:13px;&quot;&quot;&gt;Churn risk&lt;/td&gt;"
    "&lt;td style=&quot;&quot;padding:6px 0;color:#0F172A;font-size:13px;&quot;&quot;&gt;&quot; &amp; churnSafe &amp; &quot;&lt;/td&gt;&lt;/tr&gt;&quot;)&#xA;"
    "    sb.AppendLine(&quot;    &lt;tr&gt;&lt;td style=&quot;&quot;padding:6px 0;color:#64748B;font-size:13px;&quot;&quot;&gt;Customer tier&lt;/td&gt;"
    "&lt;td style=&quot;&quot;padding:6px 0;color:#0F172A;font-size:13px;&quot;&quot;&gt;&quot; &amp; tierSafe &amp; &quot;&lt;/td&gt;&lt;/tr&gt;&quot;)&#xA;"
    "    sb.AppendLine(&quot;    &lt;tr&gt;&lt;td style=&quot;&quot;padding:6px 0;color:#64748B;font-size:13px;&quot;&quot;&gt;Health score&lt;/td&gt;"
    "&lt;td style=&quot;&quot;padding:6px 0;color:#0F172A;font-size:13px;&quot;&quot;&gt;&quot; &amp; healthSafe &amp; &quot;&lt;/td&gt;&lt;/tr&gt;&quot;)&#xA;"
    "    sb.AppendLine(&quot;    &lt;tr&gt;&lt;td style=&quot;&quot;padding:6px 0;color:#64748B;font-size:13px;&quot;&quot;&gt;Renewal term (mo)&lt;/td&gt;"
    "&lt;td style=&quot;&quot;padding:6px 0;color:#0F172A;font-size:13px;&quot;&quot;&gt;&quot; &amp; termSafe &amp; &quot;&lt;/td&gt;&lt;/tr&gt;&quot;)&#xA;"
    "    sb.AppendLine(&quot;    &lt;tr&gt;&lt;td style=&quot;&quot;padding:6px 0;color:#64748B;font-size:13px;&quot;&quot;&gt;Competitor&lt;/td&gt;"
    "&lt;td style=&quot;&quot;padding:6px 0;color:#0F172A;font-size:13px;&quot;&quot;&gt;&quot; &amp; compSafe &amp; &quot;&lt;/td&gt;&lt;/tr&gt;&quot;)&#xA;"
    "    If Not String.IsNullOrWhiteSpace(requester) Then sb.AppendLine"
)
if old_rows not in text:
    raise SystemExit("HTML approver row not found")
text = text.replace(old_rows, new_rows, 1)

# --- Slack: after ratDisplay, add fd reads from in_ApprovalBodyJson (parse once) ---
# Simpler: add in_Churn etc as InvokeCode args from workflow - avoids parsing twice in VB
# Instead patch Slack code to parse jo once for extra fields after ratDisplay line

slack_needle = (
    "        Dim ratDisplay As String = If(String.IsNullOrWhiteSpace(ratSafe) OrElse ratSafe = &quot;N/A&quot;, "
    "&quot;_not provided_&quot;, ratSafe)&#xA;        Dim msgPayload As String = "
)
slack_insert = (
    "        Dim ratDisplay As String = If(String.IsNullOrWhiteSpace(ratSafe) OrElse ratSafe = &quot;N/A&quot;, "
    "&quot;_not provided_&quot;, ratSafe)&#xA;"
    "        Dim churnS As String = &quot;&quot;, tierS As String = &quot;&quot;, healthS As String = &quot;&quot;, termS As String = &quot;&quot;, compS As String = &quot;&quot;&#xA;"
    "        Try&#xA;"
    "            Dim jos = Newtonsoft.Json.Linq.JObject.Parse(in_ApprovalBodyJson)&#xA;"
    "            Dim fds = TryCast(jos(&quot;formData&quot;), Newtonsoft.Json.Linq.JObject)&#xA;"
    "            If fds IsNot Nothing Then&#xA;"
    "                If fds(&quot;churn_risk&quot;) IsNot Nothing Then churnS = fds(&quot;churn_risk&quot;).ToString()&#xA;"
    "                If fds(&quot;customer_tier&quot;) IsNot Nothing Then tierS = fds(&quot;customer_tier&quot;).ToString()&#xA;"
    "                If fds(&quot;health_score&quot;) IsNot Nothing Then healthS = fds(&quot;health_score&quot;).ToString()&#xA;"
    "                If fds(&quot;renewal_term_months&quot;) IsNot Nothing Then termS = fds(&quot;renewal_term_months&quot;).ToString()&#xA;"
    "                If fds(&quot;competitor_involved&quot;) IsNot Nothing Then compS = fds(&quot;competitor_involved&quot;).ToString()&#xA;"
    "            End If&#xA;"
    "        Catch ex2 As Exception&#xA;"
    "        End Try&#xA;"
    "        churnS = churnS.Replace(&quot;&quot;&quot;&quot;, &quot;&quot;).Replace(System.Environment.NewLine, &quot; &quot;)&#xA;"
    "        tierS = tierS.Replace(&quot;&quot;&quot;&quot;, &quot;&quot;).Replace(System.Environment.NewLine, &quot; &quot;)&#xA;"
    "        healthS = healthS.Replace(&quot;&quot;&quot;&quot;, &quot;&quot;).Replace(System.Environment.NewLine, &quot; &quot;)&#xA;"
    "        termS = termS.Replace(&quot;&quot;&quot;&quot;, &quot;&quot;).Replace(System.Environment.NewLine, &quot; &quot;)&#xA;"
    "        compS = compS.Replace(&quot;&quot;&quot;&quot;, &quot;&quot;).Replace(System.Environment.NewLine, &quot; &quot;)&#xA;"
    "        Dim msgPayload As String = "
)

if slack_needle not in text:
    raise SystemExit("Slack ratDisplay needle not found")
text = text.replace(slack_needle, slack_insert, 1)

# Expand Slack fields array: after Approval ID field, add 5 mrkdwn fields (second section)
slack_old = (
    "&quot;{&quot;&quot;type&quot;&quot;:&quot;&quot;mrkdwn&quot;&quot;,&quot;&quot;text&quot;&quot;:&quot;&quot;*Approval ID:*\\n&quot; &amp; in_ApprovalId &amp; &quot;&quot;&quot;}]},&quot; &amp;&#xA;"
    "            &quot;{&quot;&quot;type&quot;&quot;:&quot;&quot;section&quot;&quot;,&quot;&quot;text&quot;&quot;:{&quot;&quot;type&quot;&quot;:&quot;&quot;mrkdwn&quot;&quot;,&quot;&quot;text&quot;&quot;:&quot;&quot;:memo: *Rationale:* "
)
slack_new = (
    "&quot;{&quot;&quot;type&quot;&quot;:&quot;&quot;mrkdwn&quot;&quot;,&quot;&quot;text&quot;&quot;:&quot;&quot;*Approval ID:*\\n&quot; &amp; in_ApprovalId &amp; &quot;&quot;&quot;},&quot; &amp;&#xA;"
    "            &quot;{&quot;&quot;type&quot;&quot;:&quot;&quot;mrkdwn&quot;&quot;,&quot;&quot;text&quot;&quot;:&quot;&quot;*Churn risk:*\\n&quot; &amp; churnS &amp; &quot;&quot;&quot;},&quot; &amp;&#xA;"
    "            &quot;{&quot;&quot;type&quot;&quot;:&quot;&quot;mrkdwn&quot;&quot;,&quot;&quot;text&quot;&quot;:&quot;&quot;*Customer tier:*\\n&quot; &amp; tierS &amp; &quot;&quot;&quot;},&quot; &amp;&#xA;"
    "            &quot;{&quot;&quot;type&quot;&quot;:&quot;&quot;mrkdwn&quot;&quot;,&quot;&quot;text&quot;&quot;:&quot;&quot;*Health score:*\\n&quot; &amp; healthS &amp; &quot;&quot;&quot;},&quot; &amp;&#xA;"
    "            &quot;{&quot;&quot;type&quot;&quot;:&quot;&quot;mrkdwn&quot;&quot;,&quot;&quot;text&quot;&quot;:&quot;&quot;*Renewal term (mo):*\\n&quot; &amp; termS &amp; &quot;&quot;&quot;},&quot; &amp;&#xA;"
    "            &quot;{&quot;&quot;type&quot;&quot;:&quot;&quot;mrkdwn&quot;&quot;,&quot;&quot;text&quot;&quot;:&quot;&quot;*Competitor:*\\n&quot; &amp; compS &amp; &quot;&quot;&quot;}]},&quot; &amp;&#xA;"
    "            &quot;{&quot;&quot;type&quot;&quot;:&quot;&quot;section&quot;&quot;,&quot;&quot;text&quot;&quot;:{&quot;&quot;type&quot;&quot;:&quot;&quot;mrkdwn&quot;&quot;,&quot;&quot;text&quot;&quot;:&quot;&quot;:memo: *Rationale:* "
)
if slack_old not in text:
    raise SystemExit("Slack fields block not found")
text = text.replace(slack_old, slack_new, 1)

XAML.write_text(text, encoding="utf-8")
print("WaitDecision.xaml patched OK")
