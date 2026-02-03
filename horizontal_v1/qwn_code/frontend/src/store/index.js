import { createStore } from 'pinia';

const store = createStore({
  state: () => ({
    user: null,
    isAuthenticated: false
  }),
  mutations: {
    SET_USER(state, user) {
      state.user = user;
      state.isAuthenticated = !!user;
    }
  },
  actions: {
    setUser({ commit }, user) {
      commit('SET_USER', user);
    }
  }
});

export default store;