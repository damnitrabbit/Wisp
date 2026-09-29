// The 8-bit rabbit. Eyes blink, mouth nibbles. mode: 'awake' | 'look' (searching) | 'sleep' (offline)
const BLINK = { values: '6;6;1;6;6', y: '2;2;4.5;2;2', keyTimes: '0;0.92;0.95;0.98;1', dur: '4.5s' };

function Eye({ x }) {
  return (
    <rect x={x} y="2" width="6" height="6">
      <animate attributeName="height" values={BLINK.values} keyTimes={BLINK.keyTimes} dur={BLINK.dur} repeatCount="indefinite" />
      <animate attributeName="y" values={BLINK.y} keyTimes={BLINK.keyTimes} dur={BLINK.dur} repeatCount="indefinite" />
    </rect>
  );
}

function Mouth({ animate = true }) {
  return (
    <>
      <rect x="9.5" y="12" width="1" height="1" />
      <rect x="11.5" y="12" width="1" height="1" />
      <rect x="13.5" y="12" width="1" height="1" />
      <rect x="10.5" y="13" width="1" height="1" />
      <rect x="12.5" y="13" width="1" height="1" />
      {animate && (
        <animateTransform attributeName="transform" type="translate" values="0 0;0 -0.5;0 0;0 -0.5;0 0;0 0" keyTimes="0;0.55;0.6;0.65;0.7;1" dur="3.2s" repeatCount="indefinite" calcMode="discrete" />
      )}
    </>
  );
}

export default function Rabbit({ className = 'rabbit-sm', mode = 'awake', label = 'NoTrace rabbit' }) {
  if (mode === 'sleep') {
    return (
      <svg className={className} viewBox="0 0 24 18" shapeRendering="crispEdges" role="img" aria-label="Sleeping rabbit">
        <g fill="#5E5E5E">
          <rect x="2" y="6" width="6" height="1" />
          <rect x="16" y="6" width="6" height="1" />
          <Mouth animate={false} />
        </g>
      </svg>
    );
  }
  return (
    <svg className={className} viewBox="0 0 24 18" shapeRendering="crispEdges" role="img" aria-label={label}>
      <g fill="#E6E3D8">
        <Eye x="2" />
        <Eye x="16" />
        {mode === 'look' && (
          <animateTransform attributeName="transform" type="translate" values="0 0;-1 0;-1 0;1 0;1 0;0 0" keyTimes="0;0.1;0.4;0.5;0.85;1" dur="3.6s" repeatCount="indefinite" calcMode="discrete" />
        )}
      </g>
      <g fill="#E6E3D8">
        <Mouth />
      </g>
    </svg>
  );
}
