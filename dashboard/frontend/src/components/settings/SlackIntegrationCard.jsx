import { useState, useEffect } from 'react';
import { CheckCircle2, XCircle, Send, Loader2 } from 'lucide-react';
import { getSlackStatus, sendSlackTest } from '../../api/client';

const StatusRow = ({ label, ok, value }) => (
    <div className="flex items-center justify-between py-3 first:pt-1 last:pb-1 text-sm">
        <span className="font-medium text-slate-200">{label}</span>
        <span className="flex items-center gap-1.5">
            {ok ? (
                <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400" />
            ) : (
                <XCircle className="h-3.5 w-3.5 text-rose-400" />
            )}
            <span
                className={`font-mono text-xs sm:text-sm ${ok ? 'text-slate-400' : 'text-rose-300'}`}
            >
                {value}
            </span>
        </span>
    </div>
);

const SlackIntegrationCard = () => {
    const [status, setStatus] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [testing, setTesting] = useState(false);
    const [testResult, setTestResult] = useState(null); // { ok, message }

    useEffect(() => {
        let cancelled = false;
        getSlackStatus()
            .then((data) => !cancelled && setStatus(data))
            .catch((err) => !cancelled && setError(err.message))
            .finally(() => !cancelled && setLoading(false));
        return () => {
            cancelled = true;
        };
    }, []);

    const handleTest = async () => {
        setTesting(true);
        setTestResult(null);
        try {
            await sendSlackTest();
            setTestResult({ ok: true, message: 'Test message sent. Check your Slack channel.' });
        } catch (err) {
            setTestResult({ ok: false, message: err.message });
        } finally {
            setTesting(false);
        }
    };

    return (
        <div className="rounded-xl border border-slate-800/80 bg-slate-900/60 p-5 shadow-lg backdrop-blur-sm">
            <div className="mb-4 flex items-center justify-between">
                <h2 className="text-xs font-semibold uppercase tracking-wider text-slate-400">
                    SLACK APPROVALS
                </h2>
                {status && (
                    <span
                        className={`rounded-full border px-2.5 py-0.5 text-xs font-medium ${status.can_notify && status.can_receive_actions
                                ? 'border-emerald-500/30 bg-emerald-500/15 text-emerald-400'
                                : 'border-amber-500/30 bg-amber-500/15 text-amber-400'
                            }`}
                    >
                        {status.can_notify && status.can_receive_actions ? 'Connected' : 'Setup needed'}
                    </span>
                )}
            </div>

            {loading && <p className="text-sm text-slate-400">Checking Slack connection...</p>}

            {error && (
                <div className="rounded-lg border border-red-800 bg-red-950/60 p-3 text-sm text-red-200">
                    Could not load Slack status: {error}
                </div>
            )}

            {status && (
                <>
                    <div className="divide-y divide-slate-800/60">
                        <StatusRow
                            label="Bot token"
                            ok={status.bot_token_set}
                            value={status.bot_token_set ? 'configured' : 'SLACK_BOT_TOKEN missing'}
                        />
                        <StatusRow
                            label="Channel"
                            ok={Boolean(status.channel_id)}
                            value={status.channel_id || 'SLACK_CHANNEL_ID missing'}
                        />
                        <StatusRow
                            label="Signing secret (button clicks)"
                            ok={status.signing_secret_set}
                            value={status.signing_secret_set ? 'configured' : 'SLACK_SIGNING_SECRET missing'}
                        />
                    </div>

                    <div className="mt-4 flex flex-wrap items-center gap-3">
                        <button
                            type="button"
                            onClick={handleTest}
                            disabled={!status.can_notify || testing}
                            className="flex items-center gap-2 rounded-lg bg-indigo-500 px-4 py-2 text-sm font-semibold text-white shadow-md shadow-indigo-500/20 transition-all hover:bg-indigo-400 active:scale-95 disabled:cursor-not-allowed disabled:opacity-40 cursor-pointer"
                        >
                            {testing ? (
                                <Loader2 className="h-4 w-4 animate-spin" />
                            ) : (
                                <Send className="h-4 w-4" />
                            )}
                            <span>Send test message</span>
                        </button>

                        {testResult && (
                            <span className={`text-xs ${testResult.ok ? 'text-emerald-400' : 'text-rose-400'}`}>
                                {testResult.message}
                            </span>
                        )}
                    </div>

                    {!status.can_notify && (
                        <p className="mt-3 text-xs text-slate-500">
                            Set the missing values in the backend .env and restart the API.
                        </p>
                    )}
                </>
            )}
        </div>
    );
};

export default SlackIntegrationCard;