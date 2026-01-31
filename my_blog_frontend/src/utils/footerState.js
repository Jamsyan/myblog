import { ref, computed, watch } from 'vue';

const footerVisible = ref(false);
const footerHeight = ref(0);
const subscribers = new Set();

const calculateDynamicSpacing = () => {
  const spacing = Math.round(window.innerHeight * 0.01);
  return Math.min(spacing, 15);
};

export function useFooterState() {
  const isVisible = computed(() => footerVisible.value);
  const height = computed(() => footerHeight.value);
  const offset = computed(() => {
    if (!footerVisible.value) return 0;
    return footerHeight.value + calculateDynamicSpacing();
  });

  const setFooterVisible = (visible) => {
    footerVisible.value = visible;
    notifySubscribers();
  };

  const setFooterHeight = (height) => {
    footerHeight.value = height;
    notifySubscribers();
  };

  const subscribe = (callback) => {
    subscribers.add(callback);
    return () => subscribers.delete(callback);
  };

  const notifySubscribers = () => {
    subscribers.forEach(callback => {
      callback({
        visible: footerVisible.value,
        height: footerHeight.value,
        offset: offset.value
      });
    });
  };

  return {
    isVisible,
    height,
    offset,
    setFooterVisible,
    setFooterHeight,
    subscribe
  };
}

export function useFooterSubscriber(callback) {
  const { subscribe } = useFooterState();
  
  const unsubscribe = subscribe(callback);
  
  return {
    unsubscribe
  };
}
