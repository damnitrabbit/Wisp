// Room names in the paper style: lower case, themes as fragments.
export const roomTitle = (c) => String(c?.name ?? '').toLowerCase();
export const roomTheme = (c) => {
  const b = String(c?.blurb ?? '').trim().replace(/\.$/, '');
  return b ? b[0].toLowerCase() + b.slice(1) : '';
};
