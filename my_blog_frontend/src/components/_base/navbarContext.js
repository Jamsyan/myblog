import { ref, computed, provide, inject } from 'vue';

const NAVBAR_CONTEXT_KEY = Symbol('navbarContext');

export function provideNavbarContext() {
  const isCollapsed = ref(false);
  const actions = ref([]);
  const title = ref('');

  const setCollapsed = (collapsed) => {
    isCollapsed.value = collapsed;
  };

  const setActions = (newActions) => {
    actions.value = newActions;
  };

  const setTitle = (newTitle) => {
    title.value = newTitle;
  };

  const context = {
    isCollapsed: computed(() => isCollapsed.value),
    actions: computed(() => actions.value),
    title: computed(() => title.value),
    setCollapsed,
    setActions,
    setTitle
  };

  provide(NAVBAR_CONTEXT_KEY, context);

  return context;
}

export function useNavbarContext() {
  const context = inject(NAVBAR_CONTEXT_KEY);

  if (!context) {
    throw new Error('useNavbarContext must be used within a component that provides navbar context');
  }

  return context;
}

export function useNavbarActions() {
  const context = useNavbarContext();

  const registerActions = (newActions) => {
    context.setActions(newActions);
  };

  const clearActions = () => {
    context.setActions([]);
  };

  const setNavbarTitle = (newTitle) => {
    context.setTitle(newTitle);
  };

  const collapseNavbar = () => {
    context.setCollapsed(true);
  };

  const expandNavbar = () => {
    context.setCollapsed(false);
  };

  return {
    registerActions,
    clearActions,
    setNavbarTitle,
    collapseNavbar,
    expandNavbar,
    isCollapsed: context.isCollapsed,
    actions: context.actions,
    title: context.title
  };
}
