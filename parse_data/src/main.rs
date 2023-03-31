use serde_json::Value;

struct Config {
    jsonl_path: String,
    source_path: String,
    target_path: String,
}
impl Config {
    fn build(args: &mut Vec<String>) -> Result<Self, &'static str> {
        Ok(Config {
            jsonl_path: match args.get(1) {
                Some(q) => q.to_owned(),
                None => return Err("Provide a path to jsonl file."),
            },
            source_path: match args.get(2) {
                Some(fp) => fp.to_owned(),
                None => return Err("Provide a path to save source file."),
            },
            target_path: match args.get(3) {
                Some(fp) => fp.to_owned(),
                None => return Err("Provide a path to save target file."),
            },
        })
    }
}

fn main() {
    let config =
        Config::build(&mut std::env::args().collect::<Vec<String>>()).unwrap_or_else(|e| {
            eprintln!("Something went wrong parsing args with error {}", e);
            std::process::exit(1);
        });
    let file_content = std::fs::read_to_string(&config.jsonl_path).unwrap_or_else(|e| {
        eprintln!("Something went wrong with error {}", e);
        std::process::exit(1);
    });

    let mut json_lines: Vec<Value> = Vec::with_capacity(file_content.len());
    for line in file_content.lines() {
        json_lines.push(serde_json::from_str(line).unwrap_or_else(|e| {
            eprintln!("Something went wrong converting to json with error {}", e);
            std::process::exit(1);
        }));
    }

    let src = parse_text(&json_lines, false);
    let tar = parse_text(&json_lines, true);

    let mut new_src: Vec<String> = Vec::new();
    let mut new_tar: Vec<String> = Vec::new();

    for i in 0..json_lines.len() {
        if !src[i].eq(&tar[i]) {
            new_src.push(src[i].clone());
            new_tar.push(tar[i].clone());
        }
    }

    println!("src len: {}", &new_src.len());

    if let Err(e) = save_file(&config.source_path, &new_src) {
        eprintln!("path: {} err: {}", &config.source_path, e);
        std::process::exit(1);
    }
    if let Err(e) = save_file(&config.target_path, &new_tar) {
        eprintln!("path: {} err: {}", &config.target_path, e);
        std::process::exit(1);
    }
}

pub fn save_file(path: &str, data: &Vec<String>) -> Result<(), &'static str> {
    let data = data.join("\n");
    let path = match std::env::current_dir() {
        Ok(cur_dir) => {
            let cur_dir = cur_dir.join(path);
            cur_dir
                .to_str()
                .unwrap_or_else(|| {
                    eprintln!("Problem converting PathBuf to str");
                    std::process::exit(1);
                })
                .to_owned()
        }
        Err(_) => return Err("Problem reading current dir"),
    };
    match std::fs::write(&path, data) {
        Ok(_) => {
            println!("Written to {}", &path);
        }
        Err(_) => return Err("Problem writing to file"),
    };

    Ok(())
}

fn parse_text(obj_vec: &Vec<Value>, is_target: bool) -> Vec<String> {
    let special_chars = [
        "!", "\"", "#", "$", "%", "&", "'", "(", ")", "*", "+", ",", "-", ".", "/", ":", ";", "<",
        "=", ">", "?", "@", "[", "\\", "]", "^", "_", "`", "{", "|", "}", "~",
    ];

    let from = if is_target { "tgt" } else { "src" };
    let mut lines: Vec<String> = Vec::new();

    for val in obj_vec.iter() {
        let edits = val["edits"].as_array().unwrap_or_else(|| {
            eprintln!("Something went wrong parsing to array.");
            std::process::exit(1);
        });

        for edit in edits.iter() {
            if edit["is_typo"].as_bool().unwrap_or(false) {
                let mut text = edit[from]["text"]
                    .as_str()
                    .unwrap_or_else(|| {
                        eprintln!("Something went wrong parsing to string.");
                        std::process::exit(1);
                    })
                    .to_string();

                for c in special_chars {
                    text = text.replace(c, " ");
                }

                lines.push(
                    text.trim()
                        .to_lowercase()
                        .split(' ')
                        .collect::<Vec<_>>()
                        .iter()
                        .filter_map(|line| match line.is_empty() {
                            true => None,
                            false => Some(*line),
                        })
                        .collect::<Vec<_>>()
                        .join(" "),
                );
            }
        }
    }

    lines
}
