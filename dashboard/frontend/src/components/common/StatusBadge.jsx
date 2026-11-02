import { TONE_CLASSES } from '../../constants/status'

const StatusBadge = ({ label, tone = 'slate' }) => (
  <span
    className={`inline-flex items-center whitespace-nowrap rounded-full border px-2.5 py-0.5 text-[11px] font-medium ${TONE_CLASSES[tone] ?? TONE_CLASSES.slate}`}
  >
    {label}
  </span>
)

export default StatusBadge