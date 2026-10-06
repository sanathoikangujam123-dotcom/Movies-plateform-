import React, {useEffect, useState} from "react";
import {createRoot} from "react-dom/client";
import {Search, Home, Film, Bookmark, User, Play, Menu, X, ChevronRight} from "lucide-react";
import "./styles.css";

const API = import.meta.env.VITE_API_URL || "http://localhost:8000";

function App(){
  const [movies,setMovies]=useState([]);
  const [search,setSearch]=useState("");
  const [menu,setMenu]=useState(false);
  const [selected,setSelected]=useState(null);

  useEffect(()=>{ fetch(`${API}/api/movies`).then(r=>r.json()).then(d=>setMovies(d.items||[])).catch(()=>{}); },[]);

  const filtered=movies.filter(m=>m.title.toLowerCase().includes(search.toLowerCase()));

  return <div className="app">
    <header className="topbar">
      <button className="icon" onClick={()=>setMenu(true)}><Menu size={22}/></button>
      <div className="logo">MOVIE<span>HUB</span></div>
      <button className="icon"><User size={21}/></button>
    </header>

    <div className="search">
      <Search size={19}/>
      <input value={search} onChange={e=>setSearch(e.target.value)} placeholder="Search movies..."/>
    </div>

    {selected ? <MovieView movie={selected} back={()=>setSelected(null)}/> :
    <main>
      <section className="hero">
        <div className="hero-content">
          <p className="eyebrow">WELCOME TO MOVIEHUB</p>
          <h1>Unlimited stories.<br/><span>One place.</span></h1>
          <p>Discover movies and build your personal watchlist.</p>
          <button className="primary" onClick={()=>movies[0]&&setSelected(movies[0])}><Play size={17} fill="currentColor"/> Watch now</button>
        </div>
      </section>

      <section className="section">
        <div className="section-head"><h2>Featured</h2><ChevronRight size={19}/></div>
        <div className="grid">{filtered.map((m,i)=><MovieCard key={i} movie={m} onClick={()=>setSelected(m)}/>)}</div>
        {!filtered.length && <div className="empty">No movies found.</div>}
      </section>
    </main>}

    <nav className="bottom">
      <button className="active"><Home size={20}/><small>Home</small></button>
      <button><Film size={20}/><small>Movies</small></button>
      <button><Bookmark size={20}/><small>Saved</small></button>
      <button><User size={20}/><small>Profile</small></button>
    </nav>

    {menu && <div className="drawer-back" onClick={()=>setMenu(false)}>
      <aside className="drawer" onClick={e=>e.stopPropagation()}>
        <div className="drawer-head"><b>MOVIE<span>HUB</span></b><button className="icon" onClick={()=>setMenu(false)}><X/></button></div>
        <a>Home</a><a>Movies</a><a>Categories</a><a>My Watchlist</a><a>Watch History</a><a>Profile</a><hr/><a>Help & Support</a>
      </aside>
    </div>}
  </div>
}

function MovieCard({movie,onClick}){
 return <button className="card" onClick={onClick}>
   <img src={movie.poster_url} alt=""/>
   <div className="card-info"><b>{movie.title}</b><small>{movie.year||"2026"} • {movie.duration||"Movie"}</small></div>
 </button>
}
function MovieView({movie,back}){
 return <main className="detail">
   <button className="back" onClick={back}>← Back</button>
   <div className="player"><Play size={48} fill="currentColor"/></div>
   <h1>{movie.title}</h1>
   <div className="meta">{movie.category} • {movie.year||"—"} • {movie.duration||"—"}</div>
   <p>{movie.description}</p>
   <button className="primary"><Play size={17} fill="currentColor"/> Play movie</button>
 </main>
}
createRoot(document.getElementById("root")).render(<App/>);
